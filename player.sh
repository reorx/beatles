spotify=$(osascript -e '
try
    tell application "Spotify"
        set artistName to artist of current track
        set trackName to name of current track
        set albumName to album of current track
        set playerState to player state
        return artistName & " - " & trackName & " - " & albumName & "|" & playerState
    end tell
on error errText
    ""
end try
');

echo "spotify: $spotify"

itunes=$(osascript -e '
try
    tell application "iTunes"
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
');

echo "itunes: $itunes"
