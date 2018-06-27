# -*- coding: utf-8 -*-

import re
import csv


class K:
    song = 'Song'
    album = 'Album debut'
    songwriter = 'Songwriter(s)'
    vocal = 'Lead vocal(s)'
    year = 'Year'
    notes = 'Notes'
    ref = 'Ref(s)'


SUB_REGEX = re.compile(r'^([\w\s\(\),]+)((\[\d+\])+)')


def to_alfred_dict(d):
    """
    - title
    - subtitle
    - arg
    """
    song = trim_quotes(d[K.song])
    vocals = []
    for i in d[K.vocal].split('\n'):
        vocals.append(
            trim_braces(
                SUB_REGEX.sub(r'\1', i.strip()).strip()
            )
        )
    vocals_str = ', '.join(vocals)
    album_one_line = d[K.album].strip().replace('\n', ' ')
    subtitle = '{} / {} / {}'.format(vocals_str, album_one_line, d[K.year])
    return {
        'title': song,
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
    rows = []
    with open('./beatles_songs.csv', 'r') as fi:
        r = csv.DictReader(fi)
        for i in r:
            rows.append(to_alfred_dict(i))

    with open('./list_filter.csv', 'w') as fo:
        w = csv.DictWriter(fo, fieldnames=['title', 'subtitle', 'arg'])
        w.writeheader()
        for row in rows:
            w.writerow(row)


if __name__ == '__main__':
    main()
