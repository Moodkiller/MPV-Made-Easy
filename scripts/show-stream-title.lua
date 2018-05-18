-- Show OSD stream title from playlist on change
--
-- Usefull for iPTV when switching the streams/channels defined in the playlist
--
-- At the moment of jump from stream1 to stream2 the property 'media-title' still contains stream1.title
-- (see mpv doc for more details, lookup playlist/N/current, playlist/N/playing )
-- To display correct stream2.title from playlist use this script.
--
-- Note: 'media-title' property gets updated more often then switching channels.
-- Therefore the script has to validate the 'media-title', It is omplemented
-- by 'media-title' matching to cfg.valid pattern. The empty cfg.valid activates
-- 'passthrough' mode (all 'media-title' changes are valid and shown). The default
-- cfg.valid pattern should be OK, actually is based on SMPlayer fromatted playlist
--
-- Place script into ~/.config/mpv/scripts/ for autoload
--
-- OSD options like duration, alignment, border, scale could be set in ~/.config/mpv/mpv.conf
--
-- SMPlayer playlist entry example:
--   #EXTINF:0,RT News,,0
--   http://rt-eng-live.hls.adaptive.level3.net/rt/eng/index1600.m3u8
--
-- GitHub: https://github.com/blue-sky-r/mpv/tree/master/scripts

-- OSD format string tokens:
-- %N ... iPTV channel number (playlist index)
-- %t ... iPTV channel name (user friendly stream title)
-- %T ... iPTV channel name in uppercase

-- defaults
local cfg = {
    -- OSD text format
    format = "%N. %t",
    -- validate title from playlist (empty for passthrough = valid all)
    valid  = "^.+,,0$"
}

-- check if string is valid title by cfg.valid pattern
-- valid:   'CP24,,0', 'TA News,,0'
-- invalid: 'index', 'DVR', 'iptv-streams.m3u8', 'rtmp://ip'
local function is_valid_title(s)
    -- everything is valid (passthrough) if validation pattern is missing
    if not cfg.valid then return true end
    -- validate with pattern
    return string.match(s, cfg.valid)
end

-- [show_stream_title] property 'media-title' changed to 'iptv-streams.m3u8'
-- [show_stream_title] property 'media-title' changed to 'CP24,,0'
--
-- [show_stream_title] property 'media-title' changed to 'TA News,,0'
-- [show_stream_title] property 'media-title' changed to 'rtmp://eo1-gts.ta.live.cc:1945/ta-o/_definst_/livem2'
--
-- [show_stream_title] property 'media-title' changed to 'EDU,:/default-theme/openfolder.png,1'
-- [show_stream_title] property 'media-title' changed to 'History,,0'
--
-- [cplayer] Set property: file-local-options/force-media-title="index" -> 1
-- [show_stream_title] property 'media-title' changed to 'index'
--
mp.observe_property("media-title", "string",
    function(name, val)
        -- log
        mp.msg.info("property '"..name.."' changed to '"..val.."'")
        -- val can be url (redirects ?)
        if not is_valid_title(val) then return end

        -- SMPlayer playlist val = 'Title,,0'
        --          playlist val = 'Title'

        -- get comma position or entire length
        local compos = string.find(val..",", ",")
        -- stream title from val
        local title = string.sub(val, 1, compos-1)
        -- playlist index (0-based)
        local n = 1 + mp.get_property('playlist-pos')
        -- replace tokens
        local txt = string.gsub(cfg.format, '%%N', n):gsub('%%t', title):gsub('%%T', string.upper(title))

        -- osd show
        mp.osd_message(txt)
    end
)

