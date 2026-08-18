local replacements = {
    ["$FILES_BASE_URL"] = "base-url.files",
    ["$ASSETS_BASE_URL"] = "base-url.assets"
}

local function expand_url(url)
    for token, metadata_key in pairs(replacements) do
        if url:find(token, 1, true) then
            local value = quarto.metadata.get(metadata_key)

            if value ~= nil then
                local base_url = pandoc.utils.stringify(value)

                -- Prevent // when the configured base URL ends with /
                base_url = base_url:gsub("/+$", "")
                local escaped_token = token:gsub("(%W)", "%%%1")

                url = url:gsub(
                    escaped_token,
                    function()
                        return base_url
                    end
                )
            end
        end
    end

    return url
end

local function process_metadata(value)
    if type(value) ~= "table" then
        return value
    end

    for key, child in pairs(value) do
        if key == "href" then
            local href = pandoc.utils.stringify(child)
            value[key] = pandoc.MetaString(expand_url(href))
        elseif type(child) == "table" then
            process_metadata(child)
        end
    end

    return value
end

function Meta(meta)
    return process_metadata(meta)
end

function Link(link)
    link.target = expand_url(link.target)
    return link
end

function Image(image)
    image.src = expand_url(image.src)
    return image
end