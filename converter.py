# -*- coding: utf-8 -*-

import os
import csv
import json
from format_data import read_songs_wikipedia, to_song_dict


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


ALFRED_CSV_PATH = './plugins/alfred/list_filter.csv'
PY_CLI_PATH = './beatles_song/beatles_song.py'
PY_CLI_TMPL_PATH = './beatles_song/code_template.txt'


def main():
    py_cli_version = os.environ.get('PY_CLI_VERSION', '0.1.0')
    sd_list = []
    rows = []
    for i in read_songs_wikipedia():
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
