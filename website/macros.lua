function Math(el)
    if el.text:find("\\uuline", 1, true) then
        el.text =
            "\\def\\uuline#1{\\underline{\\underline{#1}}}"
            .. el.text
        end
    return el
end