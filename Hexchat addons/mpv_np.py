# requires Python 3
from abc import ABCMeta, abstractmethod
import json
import os.path
import socket
import sys
import time

import hexchat


__module_name__ = "mpv now playing (MK Mod)"
__module_version__ = "0.4.5"
__module_description__ = "Announces info of the currently loaded 'file' in mpv"

# # Configuration Part 1, Part 2 is at the end of this script  # # # # # # # # # # # # # # # # # # #

# Paths to mpv's IPC socket or named pipe.
# Set the same path in your mpv.conf `input-ipc-server` setting
# or adjust these values.
WIN_PIPE_PATH = R"\\.\pipe\mpvsocket"
UNIX_PIPE_PATH = "/tmp/mpv-socket"  # variables are expanded

# # The Script # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def _tempfile_path(*args, **kwargs):
    """Generate a sure-to-be-free tempfile path.

    It's hacky but it works.
    """
    import tempfile
    fd, tmpfile = tempfile.mkstemp()
    # close and delete; we only want the path
    os.close(fd)
    os.remove(tmpfile)
    return tmpfile


# If asynchronous IO was to be added,
# the Win32API would need to be used on Windows.
# Details:
# - https://msdn.microsoft.com/en-us/library/windows/desktop/aa365683%28v=vs.85%29.aspx
# Examples:
# - https://msdn.microsoft.com/en-us/library/windows/desktop/aa365690%28v=vs.85%29.aspx
# - https://msdn.microsoft.com/en-us/library/windows/desktop/aa365592%28v=vs.85%29.aspx
# - https://github.com/mpv-player/mpv/blob/master/input/ipc-win.c
class MpvIpcClient(metaclass=ABCMeta):

    """Work with an open MPC instance via its JSON IPC.

    In a blocking way.
    Supports sending IPC commands,
    input commands (input.conf style)
    and arbitrary read/write_line calls.

    Classmethod `for_platform`
    will resolve to one of WinMpvIpcClient or UnixMpvIpcClient,
    depending on the current platform.
    """

    def __init__(self, path):
        self.path = path
        self._connect()

    @classmethod
    def for_platform(cls, platform=sys.platform, path=None):
        if platform == 'win32':
            return WinMpvIpcClient(path or WIN_PIPE_PATH)
        else:
            return UnixMpvIpcClient(path or UNIX_PIPE_PATH)

    @abstractmethod
    def _connect(self):
        pass

    @abstractmethod
    def _write_line(self):
        pass

    @abstractmethod
    def _read_line(self):
        pass

    @abstractmethod
    def close(self):
        pass

    def command(self, command, *params):
        data = json.dumps({"command": [command] + list(params)})
        self._write_line(data)
        while 1:
            # read until a result line is found (containing "error" key)
            result_line = self._read_line()
            result = json.loads(result_line)
            if 'error' in result:
                break
        if result['error'] != "success":
            raise RuntimeError("mpv returned an error", result['error'])

        return result['data']

    def input_command(self, cmd):
        """Send an input command."""
        self._write_line(cmd)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    @abstractmethod
    def expand_properties(self, fmt):
        """Expand a mpv property string using its run command and platform-specific hacks.

        Pending https://github.com/mpv-player/mpv/issues/3166
        for easier implementation.
        """
        pass


class WinMpvIpcClient(MpvIpcClient):

    def _connect(self):
        self._f = open(self.path, "w+t", newline='', encoding='utf-8')

    def _write_line(self, line):
        self._f.write(line.strip())
        self._f.write("\n")
        self._f.flush()

    def _read_line(self):
        return self._f.readline()

    def close(self):
        self._f.close()

    def expand_properties(self, fmt, timeout=5):
        """Expand a mpv property string using its run command and other hacks.

        Notably, spawn a Powershell process that writes a string to some file.
        Because of this, there are restrictions on the property string
        that will most likely *not* be met,
        but are checked for anyway.

        Since this is a polling-based approach (and unsafe too),
        a timeout mechanic is implemented
        and the wait time can be specified.
        """
        if "'" in fmt or "\\n" in fmt:
            raise ValueError("unsupported format string - may not contain `\\n` or `'`")

        tmpfile = _tempfile_path()

        # backslashes in quotes need to be escaped for mpv
        self.input_command(R'''run powershell.exe -Command "'{fmt}' | Out-File '{tmpfile}'"'''
                           .format(fmt=fmt, tmpfile=tmpfile.replace("\\", "\\\\")))

        # some tests reveal an average time requirement of 0.35s
        start_time = time.time()
        end_time = start_time + timeout
        while time.time() < end_time:
            if not os.path.exists(tmpfile):
                continue
            try:
                with open(tmpfile, 'r', encoding='utf-16 le') as f:  # Powershell writes utf-16 le
                    # Because we open the file faster than powershell writes to it,
                    # wait until there is a newline in out tmpfile (which powershell writes).
                    # This means we can't support newlines in the fmt string,
                    # but who needs those anyway?
                    buffer = ''
                    while time.time() < end_time:
                        result = f.read()
                        buffer += result
                        if "\n" in result:
                            # strip BOM and next line
                            buffer = buffer.lstrip("\ufeff").splitlines()[0]
                            return buffer
                        buffer += result
            except OSError:
                continue
            else:
                break
            finally:
                os.remove(tmpfile)


class UnixMpvIpcClient(MpvIpcClient):

    buffer = b""

    def _connect(self):
        self._sock = socket.socket(socket.AF_UNIX)
        self.expanded_path = os.path.expanduser(os.path.expandvars(self.path))
        self._sock.connect(self.expanded_path)

    def _write_line(self, line):
        self._sock.sendall(line.strip().encode('utf-8'))
        self._sock.send(b"\n")

    def _read_line(self):
        while 1:
            if b"\n" in self.buffer:
                line, _, self.buffer = self.buffer.partition(b"\n")
                return line.decode('utf-8')
            self.buffer += self._sock.recv(4096)

    def close(self):
        self._sock.close()

    def expand_properties(self, fmt):
        return NotImplemented


###############################################################################
# # Configuration Part 2
###############################################################################

# convert MiB to MB for example and remove the space: i.e 35 MiB -> 37MB
def prettiBytesSize(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1000.0:
            return '%3.1f%s%s' % (num, unit, suffix)
        num /= 1000.0
    return '%.1f%s%s' % (num, 'Yi', suffix)

# convert mbps and remove the space after number: i.e 1.098 mbps -> 1098mbps. This can also be changed to 1.1MB/s for eg
def prettiBytesRate(num, suffix='s'):
    for unit in ['', 'Kbp', 'Mbp', 'Gbp']:
        if abs(num) < 10000.0:
            return '%3.1f%s%s' % (num, unit, suffix)
        num /= 1000.0
    return '%.1f%s%s' % (num, 'Yi', suffix)
	
# Windows only:
# The command that is being executed.
# Supports mpv's property expansion:
# https://mpv.io/manual/stable/#property-expansion
# https://mpv.io/manual/master/#property-list

# \x02 	bold
# \x03 	colored text
# \x1D 	italic text
# \x1F 	underlined text
# \x16 	swap background and foreground colors ("reverse video")
# \x0F 	reset all formatting
	
######## Set the format/properties for audio files ###############
audioformats = ("flac", "acc", "mp3", "ac3", "m4a", "opus", "wav", "wma", "webm", "floatp")
	
def mpv_np(caller, callee, helper):
    try:
        with MpvIpcClient.for_platform() as mpv:
            try:
                size = mpv.command("get_property", "file-size")
            except RuntimeError as e:
                error_message = e.args[1]  # Extract the error message from the exception
                if "property unavailable" in error_message:
                    size = None
                else:
                    raise

            BitRate = mpv.command("get_property", "audio-bitrate")
            fileformat = mpv.command("get_property", "file-format")
            
            if fileformat in audioformats:
                command = mpv.expand_properties("me is listening to \x0307\x02${metadata/artist}\x0F - \x0307\x02${media-title}\x0F {" + prettiBytesSize(size) + " • " + fileformat.upper() + " " + prettiBytesRate(BitRate) + " • ${audio-params/channel-count}ch} • [${time-pos}${!duration==0: / ${duration}}] playing in \x0306${mpv-version}\x0F")
            if size is None:
                size_str = ""  # Or any other string you prefer to represent "not available"
                command = mpv.expand_properties("me is streaming: \x0307\x02${media-title}\x0F • [${time-pos}${!duration==0: / ${duration}}] in \x0306${mpv-version}\x0F")
            else:
                size_str = prettiBytesSize(size)
                command = mpv.expand_properties("me is watching: \x0307\x02${media-title}\x0F • " + prettiBytesSize(size) + " • [${time-pos}${!duration==0: / ${duration}}] in \x0306${mpv-version}\x0F")
                command = mpv.expand_properties("me is watching: \x0307\x02${filename}\x0F • " + prettiBytesSize(size) + " • [${time-pos}${!duration==0: / ${duration}}] in \x0306${mpv-version}\x0F")

            if command is None:
                print("Unable to expand property string - falling back to legacy")
                command = NotImplemented

            if command is NotImplemented:
                title = mpv.command("get_property", "media-title")
                command = LEGACY_CMD_FMT.format(title=title)

            hexchat.command(command)

    except OSError:
        # import traceback; traceback.print_exc()
        print("mpv IPC not running or bad configuration (see /help mpv)")

    return hexchat.EAT_ALL



if __name__ == '__main__':
    help_str = (
        "Usage: /mpv\n"
        "Setup: set `input-ipc-server={path}` in your mpv.conf file "
        "(or adjust the path in the script source)."
        .format(path=WIN_PIPE_PATH if sys.platform == 'win32' else UNIX_PIPE_PATH)
    )
    hexchat.hook_command("mpv", mpv_np, help=help_str)
    print(__module_name__, __module_version__, "loaded")
