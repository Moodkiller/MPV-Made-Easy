# MPV - Made Easy!

# Feature List:

* Similar feel and behaviour to MPC-HC (shortcut keys and mouse buttons) :
     * a - Toggles audio track.
     * s - Toggles subtitle track.
     * Spacebar / Mouse right-click - Toggle pause.
     * Mouse side-buttons (if applicable) - Skip through chapter markers (forward/backward).
     * Left/Right arrow keys - Seek ~10 seconds forward/backwards
     * Up/Down arrow keys & Mouse wheel - Increase/decrease volume by 5
     * Shift+S - Take screenshots (with subtitles).
     * Ctrl+s - Take screenshots (no subtitles).
     * Ctrl+o - Full-featured Open file box.
     * Ctrl+g - Go to a specified timestamp.
     * Ctrl+p - Show current playlist.
        * Up/down arrows - highlight / scroll through playlist.
        * Enter - Select / play highlighted file.
        * Ctrl+Shift+p - Shuffle playlist (again to sort alphabetically).
        * Shift+p - add files in currently playing directory to the playlist.
* Screen-shots are placed in the root videos directory under a new folder called "Screens" (can be changed within `mpv.conf`).
* Visualiser for audio tracks.
* Remember video position of previous played file (video/audio).
* Lightweight (no heavy filters or extra programes required).
* Adjusted OSC (On Screen Controller) to have a smaller footprint and be more practical than the default mpv varient.
* Play next sequential file in the current files folder.
* YouTube URL player (drag and drop only)
* More as I remember them...


# Installation:

One of the nicest features of MPV is that it requires no installation and can be run from its own folder (portable).
1. Clone or download this repo.
2. Unzip to your desired location.
3. Run updater.bat (this will download the latest MPV GUI build from the source stated below and youtube-dl if you pressed 'y' when prompted).
4. Optional: Run installer/mpv-install.bat as administrator to set file associations.



# Hexchat Integration:

Hexchats latest version (2.14.1) doesn't have any built in "now playing" plugins to use. And as of this version, the default MPC-HC "now-playing" script doesn't function. I have included a modified version of an MPV now playing script from github user, FichteFoll, in this pack. A prerequisite, Python 3.6 needs to be enabled/selected when you install Hexchat. If you have Hexchat already installed, no problem, just re-run the installer and choose Python 3.x from the Custom Installation screen (right at the bottom).

1. Right-click and copy the file 'mpv_np.py' (located in 'Hexchat plugin') from the downloaded pack.
2. Press the Windows key+R and type '%APPDATA%\HexChat' and press enter.
3. Paste the copied file into the 'addons' folder.
4. In Hexchat go to Window > Plugins and Scripts > Load and browse to your addons folder where you pasted 'mpv_np.py'. Normally this is 'C:\Users\moodkiller\AppData\Roaming\HexChat\addons'
5. You  should get confirmation to say the plugin has been loaded successfully.
6. Type /mpv in any window while playing a file in MPV and it should spit out something like "Moodkiller is playing: [MK] Kiznaiver - 01 [BD 1080p][Hi10][Dual-Audio] • 1.945 GiB • [00:05:48 / 00:24:03] in mpv 0.29.0-107-gd6d6da4711" for video and "Moodkiller is listening to Garnidelia - 21248931 {37.627 MiB • flac 1.091 mbps 2ch} • [00:00:51 / 00:04:17] playing in mpv 0.29.0-107-gd6d6da4711" for audio (with colour formatting).

# Screenshots
![alt text](https://i.imgur.com/GlXp12f.png "Open file window")

![alt text](https://i.imgur.com/MphDKcp.png "OSC overview, Thumbnail preview, seek bar, volume bar, window title")

![alt text](https://i.imgur.com/nomUrXt.png "Seek to specified timestamp")

![alt text](https://i.imgur.com/xB3cbkY.png "HexChat 2.14.x now playing plugin")

# Resources:
   GUI build: https://sourceforge.net/projects/mpv-player-windows/files/  
   Collection of user scripts: https://github.com/mpv-player/mpv/wiki/User-Scripts  
   MPV properties page: https://mpv.io/manual/master/#synopsis

Thanks goes to all those involved for testing and their inputs for getting stuff running. 
