# requires Python 3
from abc import ABCMeta, abstractmethod
import json
import os.path
import socket
import sys
import time

import hexchat


__module_name__ = "mpv now playing (MK Mod)"
__module_version__ = "0.4.2"
__module_description__ = "Announces info of the currently loaded 'file' in mpv"

# # Configuration # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Paths to mpv's IPC socket or named pipe.
# Set the same path in your mpv.conf `input-ipc-server` setting
# or adjust these values.
WIN_PIPE_PATH = R"\\.\pipe\mpvsocket"
UNIX_PIPE_PATH = "/tmp/mpv-socket"  # variables are expanded

# Windows only:
# The command that is being executed.
# Supports mpv's property expansion:
# https://mpv.io/manual/stable/#property-expansion
CMD_FMT = R'me is playing: 07${filename} ◘ ${file-size} ◘ [${time-pos}${!duration==0: / ${duration}}] in 06${mpv-version}'
#CMD_FMT = R'me is playing: ${media-title} [${time-pos}${!duration==0: / ${duration}}]'


# On UNIX, the above is not supported yet
# and this Python format string is used instead.
# `{title}` will be replaced with the title.
LEGACY_CMD_FMT = ""
#LEGACY_CMD_FMT = "me is playing: {title} in MPV"
#LEGACY_CMD_FMT = R'me is playing: 07${filename} ◘ ${file-size} ◘ [${time-pos}${!duration==0: / ${duration}}] in 06${mpv-version}'

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


def mpv_np(caller, callee, helper):
    try:
        with MpvIpcClient.for_platform() as mpv:
            command = mpv.expand_properties(CMD_FMT)			
            if command is None:
                print("unable to expand property string - Close and reopen current media file, or try again in ~5 minutes")
                command = NotImplemented
            if command is NotImplemented:
                title = mpv.command("get_property", "media-title")				
                command = LEGACY_CMD_FMT.format(title=title)
				#command = mpv.expand_properties(CMD_FMT)
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
