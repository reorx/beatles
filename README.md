# beatles

Data and tools to enjoy The Beatles better.

## Tools

### `beatles_song`

Python cli to search The Beatles songs and get additional information.

Installation: `pip install beatles_song`

Usage:

- `bts yesterday`

- `BS_FMT='{title} - {vocals} - {year}' bts yesterday`

- `BS_MATCH_MODE=rank BS_MATCH_RATIO=0.8 BS_MATCH_LIMIT=1 bts 'the long and windy road'`

- `BS_MATCH_MODE=fuzzy BS_MATCH_LIMIT=10 bts yes`

- `BS_LIST_ALL=1 bts`

- `BS_DEBUG=1 bts yesterday`

### Alfred Workflow

### Bitbar Plugin

## Data source

- `data/songs.wikipedia.csv`

  Song data in csv format, including song title, ablum, **songwriter(s)**,
  **vocal(s)**, year.

  - Original source: https://en.wikipedia.org/wiki/List_of_songs_recorded_by_the_Beatles

  - Total items: 305 (`$('table.jquery-tablesorter').find('tr').length - 1`)

  - Converted by: http://wikitable2csv.ggor.de/
