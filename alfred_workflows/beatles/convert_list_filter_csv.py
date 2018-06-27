# -*- coding: utf-8 -*-

import re
import csv


class K:
    name = 'Song'
    album = 'Album debut'
    songwriter = 'Songwriter(s)'
    vocal = 'Lead vocal(s)'
    year = 'Year'
    notes = 'Notes'
    ref = 'Ref(s)'


SUB_REGEX = re.compile(r'^([\w\s\(\),]+)((\[\d+\])+)')


song_keys = ['name', 'album', 'songwriter', 'vocal', 'year', 'notes']


def to_song_dict(d):
    sd = {}
    for k in song_keys:
        sd[k] = d[getattr(K, k)]

    sd['name'] = trim_quotes(sd['name'])

    vocals = []
    for i in sd['vocal'].split('\n'):
        vocals.append(
            trim_braces(
                SUB_REGEX.sub(r'\1', i.strip()).strip()
            )
        )
    sd['vocal'] = ', '.join(vocals)

    sd['album'] = sd['album'].strip().replace('\n', ' ')

    return sd


def to_alfred_dict(sd):
    """
    - title
    - subtitle
    - arg
    """
    subtitle = '{} / {} / {}'.format(sd['vocal'], sd['album'], sd['year'])

    return {
        'title': sd['name'],
        'subtitle': subtitle,
        'arg': subtitle,
    }


def trim_quotes(s):
    if s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return s


def trim_braces(s):
    if s[0] == '(' and s[-1] == ')':
        return s[1:-1]
    return s


def main():
    songs = []
    rows = []
    with open('./beatles_songs.csv', 'r') as fi:
        r = csv.DictReader(fi)
        for i in r:
            sd = to_song_dict(i)
            rows.append(to_alfred_dict(sd))

    with open('./list_filter.csv', 'w') as fo:
        w = csv.DictWriter(fo, fieldnames=['title', 'subtitle', 'arg'])
        w.writeheader()
        for row in rows:
            w.writerow(row)


if __name__ == '__main__':
    main()
