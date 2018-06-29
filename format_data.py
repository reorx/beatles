# -*- coding: utf-8 -*-
"""
format wikipedia csv, provide functions to use the csv data
"""

import re
import csv


class K:
    title = 'Song'
    album = 'Album debut'
    songwriters = 'Songwriter(s)'
    vocals = 'Lead vocal(s)'
    year = 'Year'
    notes = 'Notes'
    ref = 'Ref(s)'


song_keys = ['title', 'album', 'songwriters', 'vocals', 'year', 'notes']


SUB_REGEX = re.compile(r'^([\w\s\(\),]+)((\[\d+\])+)')


def to_song_dict(d):
    sd = {}
    for k in song_keys:
        sd[k] = d[getattr(K, k)]

    vocals = []
    for i in sd['vocals'].split('\n'):
        vocals.append(
            trim_braces(
                SUB_REGEX.sub(r'\1', i.strip()).strip()
            )
        )
    sd['vocals'] = ', '.join(vocals)

    sd['album'] = sd['album'].strip().replace('\n', ' ')

    return sd


def trim_quotes(s):
    if s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return s


def trim_braces(s):
    if s[0] == '(' and s[-1] == ')':
        return s[1:-1]
    return s


DATA_CSV_PATH = './data/songs.wikipedia.csv'
DATA_CSV_SRC_PATH = './data/src/songs.wikipedia.csv'


def read_songs_wikipedia():
    print('Reading {}'.format(DATA_CSV_PATH))
    with open(DATA_CSV_PATH, 'r') as fi:
        r = csv.DictReader(fi)
        for i in r:
            yield i


def main():
    rows = []
    with open(DATA_CSV_SRC_PATH, 'r') as fi:
        r = csv.DictReader(fi)
        for i in r:
            # strip quotes in `Song` column
            i[K.title] = trim_quotes(i[K.title])

            # remove `Ref(s)` column
            del i[K.ref]

            rows.append(i)

    with open(DATA_CSV_PATH, 'w') as fo:
        w = csv.DictWriter(fo, fieldnames=[
            K.title, K.album, K.songwriters, K.vocals,
            K.year, K.notes,
        ])
        w.writeheader()
        for row in rows:
            w.writerow(row)


if __name__ == '__main__':
    main()
