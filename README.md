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

![](images/bitbar_beatles.gif)

Get it here: [itunes_beatles.10s.sh](plugins/bitbar/itunes_beatles.10s.sh)

How-to:

1. Download and put it under your BitBar plugins directory

2. Install bts by `pip install bts`

3. Make sure `bts` can be found under `/usr/local/bin` or `/usr/bin`,
   or set the execution path directly in `itunes_beatles.10s.sh` file
   (e.g. `BTS_PATH=/Users/me/.local/bin/bts`)

## Data

- `data/songs.wikipedia.csv`

  Song data in csv format, including song title, ablum, **songwriter(s)**,
  **vocal(s)**, year.

  - Original source: https://en.wikipedia.org/wiki/List_of_songs_recorded_by_the_Beatles

  - Total items: 305 (`$('.jquery-tablesorter>tbody>tr').length`)

  - Converted by: http://wikitable2csv.ggor.de/
