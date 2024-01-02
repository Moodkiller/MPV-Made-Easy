function write_properties_to_text_file()
    local properties = mp.get_property_native("property-list")
    local text = ""

    for _, prop in ipairs(properties) do
        local value = mp.get_property(prop)
        if value then
            text = text .. prop .. ": " .. value .. "\n"
        else
            text = text .. prop .. ": (no value)\n"
        end
    end

    -- Get the path to the "current_file" directory from mpv's exe location
    local current_dir = mp.command_native({"expand-path", "~~exe_dir/"})
    if current_dir then
        -- Construct the full path for the properties text file relative to the "current_file" directory
        local properties_file_path = current_dir .. "/current_file/properties.txt"
		

        -- Open the file with error checking
        local file, err = io.open(properties_file_path, "w")
        if not file then
            mp.msg.error("Failed to open the file: " .. err)
            return
        end

        -- Write the text to the file and close it
        file:write(text)
        file:close()
    else
        mp.msg.error("Failed to obtain the path to the 'current_file' directory.")
    end
end

-- Register the function to run when a file is loaded
mp.register_event("file-loaded", write_properties_to_text_file)
