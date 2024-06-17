# requires Python 3 or later
from abc import ABCMeta, abstractmethod
import json
import os.path
import socket
import sys
import time
import hexchat


__module_name__ = "mpv now playing (MK Mod)"
__module_version__ = "0.4.7"
__module_description__ = "Announces info of the currently loaded 'file' in mpv"

###############################################################################
# # Configuration Part 1
###############################################################################

# Paths to mpv's IPC socket or named pipe.
# Set the same path in your mpv.conf `input-ipc-server` setting
# or adjust these values.
WIN_PIPE_PATH = R"\\.\pipe\mpvsocket"
UNIX_PIPE_PATH = "/tmp/mpv-socket"  # variables are expanded

# The command that is being executed.
# Supports mpv's property expansion:
# https://mpv.io/manual/stable/#property-expansion

# Video Command
# To sytle this output, CTRL+F "CMD_FMT_VIDEO" and adjust it there
# CMD_FMT_VIDEO = "me is watching: \x0311\x02${filename}\x0F • ${file-size} • [${time-pos}${!duration==0: / ${duration}}] in \x0306${mpv-version}\x0F"

# Audio Command
# To sytle this output, CTRL+F "CMD_FMT_AUDIO" and adjust it there
# CMD_FMT_AUDIO = "me is listening to: \x0311\x02${metadata/artist}\x0F - \x0311\x02${media-title}\x0F (${file-size} • ${audio-bitrate} • ${audio-params/channel-count}ch) • [${time-pos}${!duration==0: / ${duration}}] in \x0306${mpv-version}\x0F"

# Stream Command 
# To sytle this output, CTRL+F "CMD_FMT_STREAM" and adjust it there

###############################################################################
# # The Script
###############################################################################

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
	

###############################################################################
# # Configuration Part 2
############################################################################### 

# HexChat message formating reference
# \x02 	bold
# \x03 	colored text
# \x1D 	italic text
# \x1F 	underlined text
# \x16 	swap background and foreground colors ("reverse video")
# \x0F 	reset all formatting

# Windows only:
# The command that is being executed.
# Supports mpv's property expansion:
# https://mpv.io/manual/stable/#property-expansion
# https://mpv.io/manual/master/#property-list

######## Set the format/properties for audio files ###############
audioformats = ("flac", "aac", "mp3", "ac3", "m4a", "opus", "wav", "wma", "webm", "floatp")

#def is_audio_playing(mpv):
    # Check if audio is playing by looking at audio bitrate
    #audio_bitrate = mpv.command("get_property", "audio-bitrate")
    #return audio_bitrate and audio_bitrate != "0"
    #print("\x0308[DEBUG] audio_bitrate (T/F):",audio_bitrate)

def mpv_np(caller, callee, helper):
    try:
        with MpvIpcClient.for_platform() as mpv:
            try:
                size = mpv.command("get_property", "file-size")
                BitRate = mpv.command("get_property", "audio-bitrate")
            except RuntimeError as e:
                error_message = e.args[1]  # Extract the error message from the exception
                if "property unavailable" in error_message:
                    size = None
                    BitRate = None
                else:
                    raise

            # Initialize variables with default values
            BitRate = "N/A"  # Default value for BitRate
            filename = "N/A"  # Default value for filename
            fileformat = "N/A"  # Default value for fileformat
            filesize = "N/A"  # Default value for filesize

            # Update variables with actual values if available
            # BitRate = mpv.command("get_property", "audio-bitrate")
            BitRate = BitRate
            filename = mpv.command("get_property", "filename")
            fileformat = mpv.command("get_property", "file-format")

            if fileformat in audioformats:
                # Audio is playing or it's an audio format
                size = prettiBytesSize(mpv.command("get_property", "file-size"))
                CMD_FMT_AUDIO = "me is listening to: \x0311\x02${metadata/artist}\x0F - \x0311\x02${media-title}\x0F (" + size + " • ${audio-bitrate} • ${audio-params/channel-count}ch) • [${time-pos}${!duration==0: / ${duration}}] in \x0306${mpv-version}\x0F"
                command = mpv.command('expand-text', CMD_FMT_AUDIO)
                
            elif size is None:
                # Unknown file format and size not available
                size_str = ""  # Or any other string you prefer to represent "not available"			
                uploader = mpv.command("get_property", "filtered-metadata").get('Uploader', None)
                CMD_FMT_STREAM = "me is streaming: \x0311\x02${media-title}\x0F - \x0311\x02" + uploader + "\x0F • [${time-pos}${!duration==0: / ${duration}}] in \x0306${mpv-version}\x0F"	
                command = mpv.command('expand-text', CMD_FMT_STREAM)
            else:
                # Likely a video
                size = prettiBytesSize(mpv.command("get_property", "file-size"))
                CMD_FMT_VIDEO = "me is watching: \x0311\x02${filename}\x0F • " + size + " • [${time-pos}${!duration==0: / ${duration}}] in \x0306${mpv-version}\x0F"
                command = mpv.command('expand-text', CMD_FMT_VIDEO)
                

            if command is None:
                print("Unable to expand property string - falling back to legacy")
                command = NotImplemented

            if command is NotImplemented:
                title = mpv.command("get_property", "filename")
                command = title

            hexchat.command(command)

    except OSError:
        import traceback
        traceback.print_exc()
        print(__module_name__ + ":\x0308 mpv IPC not running or bad configuration (see /help mpv)")

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
