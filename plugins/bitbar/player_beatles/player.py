osascript_tmpl = """\
try
    tell application "{}"
        set trackValue to name of current track
        set artistValue to artist of current track
        set albumValue to album of current track
        set playerState to player state
        return "{" ¬
            & "\"track\":" & "\"" & trackValue & "\"," ¬
            & "\"artist\":" & "\"" & artistValue & "\"," ¬
            & "\"album\":" & "\"" & albumValue & "\"," ¬
            & "\"state\":" & "\"" & playerState & "\"" ¬
            & "}"
    end tell
on error errText
    ""
end try
"""
