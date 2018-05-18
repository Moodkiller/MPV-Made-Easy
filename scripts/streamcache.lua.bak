-- streamcache.lua

-- This version of streamcache.lua has been modified a lot to reflect
-- the much different caching behaviour of more contemporary mpv versions.
-- A lua script has no more possibility to obtain the actual amount of
-- data cached by mpv - but on the other hand, mpv does do a good job
-- of maintaining a cache of "n seconds", using the "cache-secs" option.
-- Surprisingly, mpv will report only the amount of data cached in excess
-- of that many "cache-secs", when mp.get_property_native("cache-used")
-- is called.
--
-- So now, streamcachel.lua operates like this:
--  - pass the number of seconds of cache to aim for to "cache-secs"
--  - set the initial playback speed to "streamcache_min_speed" (default: 0.98)
--  - slowly (meaning: by no more than the factor of "streamcache_adjust_factor" per second)
--    decrease the playback speed only if "cache-used" reports zero kB available
--    in addition to "cache-secs" seconds of cache
--  - slowly increase the playback speed only if "cache-used" reports more
--    than "streamcache_slack/3" seconds worth of kB reported by "cache-used" available
--    in addition to "cache-secs" seconds of cache

-- Configurable parameters:
streamcache_seconds_aim = 30
streamcache_slack = 10
streamcache_min_speed = 0.98
streamcache_adjust_factor = 1.0005


-- Changing replay speed by < 2% seems to cause less
--  distortion when not correcting audio pitch (via the scaletempo filter).
-- But you can try setting this to "yes" if you like - 
--  might be useful if you want to toy around with very low min_speed values.
mp.set_property("options/audio-pitch-correction", "no")

-- Notice that using this script with non-live streams, like podcasts,
--  does usually not improve buffering, as the server will usually 
--  send pre-buffering data individually to clients, anyway. But you can
--  still use this script for podcasts where the server sends less than
--  your desired amount of pre-buffering data.

-- Anything below this line is not meant for configuration.

mp.set_property("options/cache-secs", streamcache_seconds_aim)

streamcache_cache_high = 750
streamcache_cache_low = 250
streamcache_last_kb_per_sec = 1

function streamcache_compute_cache_sizes()	

	local vb = mp.get_property_native("video-bitrate")
	if (vb == nil) then
		vb = 0
	end
	
	local ab = mp.get_property_native("audio-bitrate")
	if (ab == nil) then
		ab = 0
	end
	
	local br = vb + ab
	if (br == 0) then
		-- when we do not have plausible information on the bitrate, we
		-- first make some midly pessimistic guess of 2 MBit/s
		br = 2000000
	end

	-- compute the cache size required per second in kb
	local kb_per_sec = math.ceil(br / (8 * 1024))
	
	mp.msg.log("debug", "ab=" .. ab .. " vb=" .. vb .. " br=" .. br .. " kb_per_sec=" .. kb_per_sec .. " streamcache_last_kb_per_sec=" .. streamcache_last_kb_per_sec)

	local rate_change = kb_per_sec / streamcache_last_kb_per_sec

	if ((rate_change < 0.9) or (rate_change > 1.1)) then
		streamcache_cache_high = streamcache_slack * kb_per_sec
		streamcache_cache_low  = streamcache_cache_high / 3 
		
		mp.msg.log("v", "bitrate changed from " .. streamcache_last_kb_per_sec .. " kB/s to " .. kb_per_sec .. " kB/s, streamcache_cache_high now " .. streamcache_cache_high .. " kB") 
		
		streamcache_last_kb_per_sec = kb_per_sec 
	end		
end
mp.observe_property("audio-bitrate", "native", streamcache_compute_cache_sizes)
mp.observe_property("video-bitrate", "native", streamcache_compute_cache_sizes)

function streamcache_check_fill()
	local cache_used = mp.get_property_native("cache-used")
	if cache_used == nil then
 		cache_used = 0
	end
	
	local current_speed = mp.get_property_native("speed")
	if current_speed == nil then
 		current_speed = streamcache_min_speed
	end

	if (cache_used <= 0 or (cache_used < (streamcache_cache_high-streamcache_cache_low) and current_speed > 1.0)) then
		-- slow down, but now below streamcache_min_speed
		local new_speed = current_speed * (1.0 / streamcache_adjust_factor)
		if (new_speed < streamcache_min_speed) then
			new_speed = streamcache_min_speed
		end
		if ((new_speed > (1.0/streamcache_adjust_factor)) and (new_speed < streamcache_adjust_factor)) then
			-- new_speed is very near 1.0 - so let's use 1.0
			new_speed = 1.0
		end
		if (new_speed ~= current_speed) then
			mp.msg.log("info", "cache-used " .. cache_used .. " kB, lowered speed to " .. new_speed)
			mp.set_property("speed", new_speed)	
		end
		return
	end

	if (cache_used > streamcache_cache_high or ((cache_used > streamcache_cache_low) and current_speed < 1.0)) then
		-- speed up, but not above 1/streamcache_min_speed
		local new_speed = current_speed * streamcache_adjust_factor
		local max_speed = math.floor((10000.0/streamcache_min_speed) + 0.5)/10000.0
		if (new_speed > max_speed) then
			new_speed = max_speed
		end
		if ((new_speed > (1.0/streamcache_adjust_factor)) and (new_speed < streamcache_adjust_factor)) then
			-- new_speed is very near 1.0 - so let's use 1.0
			new_speed = 1.0
		end
		if (new_speed ~= current_speed) then
			mp.msg.log("info", "cache-used " .. cache_used .. " kB, increased speed to " .. new_speed)
			mp.set_property("speed", new_speed)	
		end
		return
	end
	
	-- cache_used is ok, and currenty speed not higher or lower 1.0	
	mp.msg.log("v", "cache-used " .. cache_used .. " kB, speed remains at " .. current_speed)	
end

streamcache_timer = mp.add_periodic_timer(1.0, streamcache_check_fill)


function streamcache_on_loaded()
	mp.msg.log("info", "new file loaded - starting with minimum speed = " .. streamcache_min_speed)
	mp.set_property("speed", streamcache_min_speed)
	streamcache_compute_cache_sizes()	
end

mp.register_event("file-loaded", streamcache_on_loaded)

