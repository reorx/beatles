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
    with open(PY_CLI_PATH, 'w') as fpy:
        songs_def = '{\n'
        for sd in sd_list:
            # keep only letter
            signature = ''.join(i for i in sd['title'] if i.isalpha()).lower()
            songs_def += '"{}": {},\n'.format(signature, json.dumps(sd, ensure_ascii=False, sort_keys=True))
        songs_def += '}'
        code = code_tmpl.format(py_cli_version, songs_def)
        fpy.write(code)


code_tmpl = """\
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
from difflib import SequenceMatcher

__version__ = '{}'

DEBUG = False
PURGE_QUERY = False
MATCH_MODE = 'rank'  # rank, fuzzy, or mixed
MATCH_LIMIT = 1
MATCH_RATIO = 0.75
FMT = '{{title}} - {{vocals}}, {{year}}'
LIST_ALL = False
SHOW_ENVS = False

global_keys = ['DEBUG', 'PURGE_QUERY', 'MATCH_MODE', 'MATCH_LIMIT', 'MATCH_RATIO', 'FMT', 'LIST_ALL', 'SHOW_ENVS']

re_brackets = re.compile(r'\([^()]+\)')

def debugp(s):
    if DEBUG:
        print('DEBUG: ' + s)

def match_songs(query, mode):
    # keep only alpha
    sig = ''.join(i for i in query if i.isalpha()).lower()
    debugp('query={{}} sig={{}}'.format(repr(query), sig))

    results = []
    for m in mode.split(','):
        results.extend(call_match_by_mode(m, sig))
    return limit_list(results, MATCH_LIMIT)

def call_match_by_mode(mode, sig):
    if mode == 'rank':
        return rank_match(sig, MATCH_RATIO, MATCH_LIMIT)
    elif mode == 'fuzzy':
        return fuzzy_match(sig, MATCH_LIMIT)
    else:
        raise ValueError('mode is not supported: ' + mode)

def precise_match(sig):
    return songs.get(sig)

def rank_match(sig, min_ratio, limit):
    s = precise_match(sig)
    if s:
        return [s]
    debugp('precise match no result')

    compares = []
    for k, s in songs.items():
        ratio = SequenceMatcher(None, k, sig).ratio()
        compares.append((ratio, s))
    compares = sorted(compares, key=lambda x: x[0], reverse=True)

    candidates = []
    for ratio, s in compares:
        if ratio > min_ratio:
            debugp('rank match candidate: {{}} {{}}'.format(ratio, s))
            candidates.append(s)
    if not candidates:
        debugp('rank match no candidates, closest match: {{}}'.format(compares[0]))
        return candidates

    debugp('rank match: total={{}} limit={{}}'.format(len(candidates), limit))
    return limit_list(candidates, limit)

def fuzzy_match(sig, limit):
    c_starts = []
    c_in = []
    for k, s in songs.items():
        if k.startswith(sig):
            c_starts.append(s)
            continue
        if sig in k:
            c_in.append(s)
            continue
    candidates = c_starts + c_in
    if not candidates:
        debugp('fuzzy match no candidates')
        return candidates
    debugp('fuzzy match: total={{}} limit={{}}'.format(len(candidates), limit))
    return limit_list(candidates, limit)

def limit_list(l, limit):
    if len(l) > limit:
        return l[:limit]
    return l

def format_output_line(s):
    return FMT.format(**s)

def purge_query(s):
    # remove brackets like `(xxx)`
    s = re_brackets.sub('', s)
    # strip
    s = s.strip()
    return s

def main():
    # update global vars by env
    for i in global_keys:
        env_key = 'BS_' + i
        globals()[i] = os.environ.get(env_key, globals()[i])
    global MATCH_LIMIT
    global MATCH_RATIO
    MATCH_LIMIT = int(MATCH_LIMIT)
    MATCH_RATIO = float(MATCH_RATIO)

    # show envs
    if SHOW_ENVS:
        print('Env vars and default value')
        for i in global_keys:
            print('  BS_{{}}\t{{}}'.format(i, globals()[i]))
        return

    # list all
    if LIST_ALL:
        for s in songs.values():
            print(format_output_line(s))
        return

    try:
        query = sys.argv[1]
    except IndexError:
        print('Usage: beatles_searcher.py <query>')
        sys.exit(1)
    if PURGE_QUERY:
        query = purge_query(query)

    debugp('global vars: MATCH_MODE={{}} MATCH_RATIO={{}} MATCH_LIMIT={{}} FMT={{}}'.format(
        MATCH_MODE, MATCH_RATIO, MATCH_LIMIT, FMT,
    ))
    # match songs
    try:
        matched = match_songs(query, MATCH_MODE)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    if not matched:
        sys.exit(1)
    for s in matched:
        print(format_output_line(s))

songs = {}

if __name__ == '__main__':
    main()
"""

if __name__ == '__main__':
    main()
