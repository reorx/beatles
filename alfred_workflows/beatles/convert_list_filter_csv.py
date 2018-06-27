# -*- coding: utf-8 -*-

import re
import csv
import json


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
    sd_list = []
    rows = []
    with open('./beatles_songs.csv', 'r') as fi:
        r = csv.DictReader(fi)
        for i in r:
            sd = to_song_dict(i)
            sd_list.append(sd)
            rows.append(to_alfred_dict(sd))

    with open('./list_filter.csv', 'w') as fo:
        w = csv.DictWriter(fo, fieldnames=['title', 'subtitle', 'arg'])
        w.writeheader()
        for row in rows:
            w.writerow(row)

    with open('./beatles_searcher.py', 'w') as fpy:
        songs_def = '{\n'
        for sd in sd_list:
            # keep only letter
            signature = ''.join(i for i in sd['name'] if i.isalpha()).lower()
            songs_def += '"{}": {},\n'.format(signature, json.dumps(sd, ensure_ascii=False))
        songs_def += '}'
        code = code_tmpl.format(songs_def)
        fpy.write(code)


code_tmpl = """\
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
from difflib import SequenceMatcher

songs = {}

re_brackets = re.compile(r'\([^()]+\)')

DEBUG = os.environ.get('BS_DEBUG', False)
MATCH_MODE = os.environ.get('BS_MATCH_MODE', 'precise')

def debugp(s):
    if DEBUG:
        print('DEBUG: ' + s)

min_ratio = 0.75

def match_song(query):
    # remove `(xxx)`
    query = re_brackets.sub('', query)
    # keep only alpha
    sig = ''.join(i for i in query if i.isalpha()).lower()
    s = songs.get(sig)
    if s:
        return s
    debugp('no direct signature match')
    compares = []
    for k, v in songs.items():
        ratio = SequenceMatcher(None, k, sig).ratio()
        compares.append((ratio, v))
    top = sorted(compares, key=lambda x: x[0], reverse=True)[0]
    debugp('closest match: {{}}'.format(top))
    if top[0] > min_ratio:
        return top[1]
    debugp('top ratio is under {{}}, nothing really matched'.format(min_ratio))

def main():
    fmt = os.environ.get('BS_FMT', '{{vocal}} - {{year}}')
    try:
        query = sys.argv[1]
    except IndexError:
        print('Usage: beatles_searcher.py <query>')
        sys.exit(1)
    s = match_song(query)
    if s:
        print(fmt.format(**s) + '|' + s['name'])
    else:
        sys.exit(1)

main()
"""

if __name__ == '__main__':
    main()
