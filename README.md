# MPV - Made Easy!

# Feature List:

* Similar feel and behaviour to MPC-HC (shortcut keys and mouse buttons) :
     * a - Toggles audio track.
     * s - Toggles subtitle track.
     * Spacebar - Toggle pause.
     * Mouse right-click - Toggle pause.
     * Mouse side-buttons (if applicable) - Skip through chapter markers.
     * Left/Right arrow keys - Seek ~10 seconds forward/backwards
     * Up/Down arrow keys  & Mouse wheel - Increase/decrease volume by 5
     * Shift+S - Take screenshots (with subtitles).
     * Ctrl+o - Full-featured open file box.
     * Ctrl+g - Go to a specified timestamp. 
* Screen-shots are placed in the root videos directory under a new folder called "Screens".
* Seek bar thumbnail preview.
* Visualiser for audio tracks.
* Remember video position of previous played file (video/audio).
* Lightweight (no heavy filters or extra filters).
* Adjusted OSC (On Screen Controller) have a smaller footprint and be more practical.
* Play next sequential file in the current files folder.
* YouTube link player (drag and drop only)
* More as I remember them...


# Installation:

One of the nicest features of MPV is that it requires no installation and can be run from its own folder (portable).
1. Clone or download this repo.
2. Run updater.bat.
3. Optional: Run installer/mpv-install.bat as administrator to set file associations.


# Hexchat Integration:

Hexchats latest version (2.14.1) doesn't have any built in "now playing" plugins to use. And as of this version, the default MPC-HC "now-playing" script doesn't function. I have included a modified version of an MPV now playing script from github user, FichteFoll, in this pack. A prerequisite, Python 3.6 needs to be enabled/selected when you install Hexchat. If you have Hexchat already installed, no problem, just re-run the installer and choose Python 3.x from the Custom Installation screen (right at the bottom).

1. Right-click and copy the file 'mpv_np.py' (located in 'Hexchat plugin') from the downloaded pack.
2. Press the Windows key+R and type '%APPDATA%\HexChat' and press enter.
3. Paste the copied file into the 'addons' folder.
4. In Hexchat go to Window > Plugins and Scripts > Load and browse to your addons folder where you pasted 'mpv_np.py'. Normally this is 'C:\Users\moodkiller\AppData\Roaming\HexChat\addons'
5. You  should get confirmation to say the plugin has been loaded successfully.
6. Type /mpv in any window while playing a file in MPV and it should spit out something like "Moodkiller is playing: [MK] Kiznaiver - 01 [BD 1080p][Hi10][Dual-Audio][05856FFC].mkv ◘ 1.945 GiB ◘ [00:04:05 / 00:24:03] in mpv 0.28.0-437-g9efb0278e7" (with colour formatting).

# Screenshots
![alt text](https://i.imgur.com/GlXp12f.png "Open file window")

![alt text](https://i.imgur.com/E0W622O.png "OSC overview, Thumbnail preview, seek bar, volume bar, window title")

![alt text](https://i.imgur.com/nomUrXt.png "Seek to specified timestamp")

![alt text](https://i.imgur.com/xB3cbkY.png "HexChat 2.14.x now playing plugin")

# Resources:
    GUI build: https://sourceforge.net/projects/mpv-player-windows/files/
    Collection of user scripts: https://github.com/mpv-player/mpv/wiki/User-Scripts
    MPV properties page: https://mpv.io/manual/master/#synopsis

Thanks goes to all those involved for testing and their inputs for getting stuff running. 
