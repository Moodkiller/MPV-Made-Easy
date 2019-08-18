loaded = false

function search_and_load_lrc()
    local lrc_path = ext2lrc(mp.get_property("path"))
    local file = io.open(lrc_path, "r")

    if file ~= nil then
        io.close(file)
        mp.set_property("sub-files", lrc_path)
		mp.set_property("sub-pos", '85')
        loaded = true
    end
end

function unload_lrc()
    if loaded == true then
        mp.set_property("sub-files", "")
		
        loaded = false
    end
end

function ext2lrc(path)
    -- strip the old extension with an empty string, then add the ".lrc" later,
    -- otherwise this will fail on files with no extension
    local name = path:gsub("(%..+)$", "")

    return name .. ".lrc"
end

mp.register_event("start-file", search_and_load_lrc)
mp.register_event("end-file", unload_lrc)