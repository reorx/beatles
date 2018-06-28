# -*- coding: utf-8 -*-

import os
import re
import csv
import json


class K:
    title = 'Song'
    album = 'Album debut'
    songwriters = 'Songwriter(s)'
    vocals = 'Lead vocal(s)'
    year = 'Year'
    notes = 'Notes'
    ref = 'Ref(s)'


SUB_REGEX = re.compile(r'^([\w\s\(\),]+)((\[\d+\])+)')


song_keys = ['title', 'album', 'songwriters', 'vocals', 'year', 'notes']


def to_song_dict(d):
    sd = {}
    for k in song_keys:
        sd[k] = d[getattr(K, k)]

    sd['title'] = trim_quotes(sd['title'])

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


def to_alfred_dict(sd):
    """
    - title
    - subtitle
    - arg
    """
    subtitle = '{} / {} / {}'.format(sd['vocals'], sd['album'], sd['year'])

    return {
        'title': sd['title'],
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

DATA_CSV_PATH = './data/songs.wikipedia.csv'
ALFRED_CSV_PATH = './plugins/alfred/list_filter.csv'
PY_CLI_PATH = './beatles_song/beatles_song.py'
PY_CLI_TMPL_PATH = './beatles_song/code_template.txt'

def main():
    py_cli_version = os.environ.get('PY_CLI_VERSION', '0.1.0')
    sd_list = []
    rows = []
    print('Reading {}'.format(DATA_CSV_PATH))
    with open(DATA_CSV_PATH, 'r') as fi:
        r = csv.DictReader(fi)
        for i in r:
            sd = to_song_dict(i)
            sd_list.append(sd)
            rows.append(to_alfred_dict(sd))
    sd_list = sorted(sd_list, key=lambda x: x['title'])

    print('Writing {}'.format(ALFRED_CSV_PATH))
    with open(ALFRED_CSV_PATH, 'w') as fo:
        w = csv.DictWriter(fo, fieldnames=['title', 'subtitle', 'arg'])
        w.writeheader()
        for row in rows:
            w.writerow(row)

    print('Writing {}'.format(PY_CLI_PATH))
    with open(PY_CLI_TMPL_PATH, 'r') as ftmpl:
        code_tmpl = ftmpl.read()
    with open(PY_CLI_PATH, 'w') as fpy:
        songs_def = '{\n'
        for sd in sd_list:
            # keep only letter
            signature = ''.join(i for i in sd['title'] if i.isalpha()).lower()
            songs_def += '"{}": {},\n'.format(signature, json.dumps(sd, ensure_ascii=False, sort_keys=True))
        songs_def += '}'
        code = code_tmpl.format(py_cli_version, songs_def)
        fpy.write(code)


if __name__ == '__main__':
    main()
