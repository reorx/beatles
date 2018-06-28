# -*- coding: utf-8 -*-

import os
import sys
import pytest
import subprocess


cli_path = os.path.join(os.path.dirname(__file__), 'beatles_song.py')


def do_cli(query, env=None, with_coverage=True):
    """
    :return: stdout
    :rtype: binary string
    """
    args = [sys.executable, cli_path, query]
    if with_coverage:
        args = ['coverage', 'run', '-a'] + args
    p = subprocess.Popen(args, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return p, out, err


testdata = [
    # rank
    ({'BS_MATCH_MODE': 'rank', 'BS_MATCH_RATIO': '0.8', 'BS_MATCH_LIMIT': '1', 'BS_FMT': '{title}|{vocals}|{year}'},
     'eight days a wee', b'Eight Days a Week|Lennon, with McCartney|1964'),
    # rank, high ratio
    ({'BS_MATCH_MODE': 'rank', 'BS_MATCH_RATIO': '1', 'BS_MATCH_LIMIT': '1', 'BS_FMT': '{title}|{vocals}|{year}'},
     'eight days a wee', None),
    # fuzzy
    ({'BS_MATCH_MODE': 'fuzzy', 'BS_MATCH_LIMIT': '3', 'BS_FMT': '{title}/{vocals}'},
     'yes', (b'Yes It Is/Lennon, McCartney and Harrison\n'
             b'Yesterday/McCartney\nLonesome Tears in My Eyes/Lennon')),
    # rank, purge
    ({'BS_MATCH_MODE': 'rank', 'BS_PURGE_QUERY': '1', 'BS_MATCH_RATIO': '0.7', 'BS_MATCH_LIMIT': '1'},
     'Norwegian Wood (This Bird Has Flown)', None),
    # rank+fuzzy, purge
    ({'BS_MATCH_MODE': 'rank,fuzzy', 'BS_PURGE_QUERY': '1', 'BS_MATCH_RATIO': '0.7', 'BS_MATCH_LIMIT': '1', 'BS_FMT': '{title} - {vocals}, {year}'},
     'Norwegian Wood (This Bird Has Flown)', b'Norwegian Wood (This Bird Has Flown) - Lennon, 1965'),
]


@pytest.mark.parametrize('env,query,want', testdata)
def test_cli(env, query, want):
    p, out, err = do_cli(query, env, with_coverage=False)
    out = out.strip()
    if want is None:
        assert p.returncode != 0
    else:
        assert out == want
        assert p.returncode == 0
