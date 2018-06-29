# beatles

Data and tools to enjoy The Beatles better.

## Tools

### `beatles_song`

Python cli to search The Beatles songs and get additional information.

Installation: `pip install beatles_song`

Usage:

- `bts yesterday`

- `BS_FMT='{title} - {vocals} - {year}' bts yesterday`

- `BS_MODE=rank BS_RATIO=0.8 BS_LIMIT=1 bts 'the long and windy road'`

- `BS_MODE=fuzzy BS_LIMIT=10 bts yes`

- `BS_LIST_ALL=1 bts`

- `BS_DEBUG=1 bts yesterday`

### Alfred Workflow

### Bitbar Plugin

## Data source

- `data/songs.wikipedia.csv`

  Song data in csv format, including song title, ablum, **songwriter(s)**,
  **vocal(s)**, year.

  - Original source: https://en.wikipedia.org/wiki/List_of_songs_recorded_by_the_Beatles

  - Total items: 305 (`$('.jquery-tablesorter>tbody>tr').length`)

  - Converted by: http://wikitable2csv.ggor.de/
