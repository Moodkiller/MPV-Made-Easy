# MPV-Made-Easy

# Feature List:

    Similar feel and behaviour to MPC-HC (shortcut keys and mouse buttons) :
        a - Toggles audio track.
        s - Toggles subtitle track.
        Spacebar - Toggle pause.
        Mouse right-click - Toggle pause.
        Mouse side-buttons (if applicable) - Skip through chapter markers.
        Shift+S - Take screenshots (with subtitles).
        Ctrl+o - Full-featured open file box.
        Ctrl+g - Go to a specified timestamp. 
    Screen-shots are placed in the root videos directory under a new folder called "Screens".
    Seek bar thumbnail preview.
    Visualiser for audio tracks.
    Remember video position of previous played file (video/audio).
    Lightweight (no heavy filters or extra filters).
    Adjusted OSC (On Screen Controller) have a smaller footprint and be more practical.
    Play next sequential file in the current files folder.
    YouTube link player (drag and drop only)
    More as I remember them...


# Installation:

One of the nicest features of MPV is that it requires no installation and can be run from its own folder (portable).

    Unzip the below folder to a detestation of your choice.
    Under the 'installer' folder, right click 'mpv-install.bat' and click 'Run as administrator' (optional - this will set file associations).


# Hexchat Integration:

Hexchats latest version (2.14.1) doesn't have any built in "now playing" plugins to use. And as of this version, the default MPC-HC "now-playing" script doesn't function. I have included a modified version of an MPV now playing script from github user, FichteFoll, in this pack. A prerequisite, Python 3.6 needs to be enabled/selected when you install Hexchat. If you have Hexchat already installed, no problem, just re-run the installer and choose Python 3.x from the Custom Installation screen (right at the bottom).

    Right-click and copy the file 'mpv_np.py' (located in 'Hexchat plugin') from the downloaded pack.
    Press the Windows key+R and type '%APPDATA%\HexChat' and press enter.
    Paste the copied file into the 'addons' folder.
    In Hexchat go to Window > Plugins and Scripts > Load and browse to your addons folder where you pasted 'mpv_np.py'. Normally this is 'C:\Users\moodkiller\AppData\Roaming\HexChat\addons'
    You  should get confirmation to say the plugin has been loaded successfully.
    Type /mpv in any window while playing a file in MPV and it should spit out something like "*Moodkiller is playing: [MK] Kiznaiver - 01 [BD 1080p][Hi10][Dual-Audio][05856FFC].mkv ◘ 1.945 GiB ◘ [00:04:05 / 00:24:03] in mpv 0.28.0-437-g9efb0278e7" (with colour formatting). 



Thanks goes to all those involved for testing and their inputs for getting stuff running. 
