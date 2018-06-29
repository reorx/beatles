#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab filetype=python

import os
import re
import sys
from difflib import SequenceMatcher

__version__ = '0.4.0'

DEBUG = False
PURGE_QUERY = False
MODE = 'rank'  # rank, fuzzy, or mixed
LIMIT = 1
RATIO = 0.75
FMT = '{title} - {vocals}, {year}'
LIST_ALL = False
SHOW_ENVS = False

global_keys = ['DEBUG', 'PURGE_QUERY', 'MODE', 'LIMIT', 'RATIO', 'FMT', 'LIST_ALL', 'SHOW_ENVS']

re_brackets = re.compile(r'\([^()]+\)')

def debugp(s):
    if DEBUG:
        print('DEBUG: ' + s)

def match_songs(query, mode):
    # keep only alpha
    sig = ''.join(i for i in query if i.isalpha()).lower()
    debugp('query={} sig={}'.format(repr(query), sig))

    results = []
    for m in mode.split(','):
        results.extend(call_match_by_mode(m, sig))
    return limit_list(results, LIMIT)

def call_match_by_mode(mode, sig):
    if mode == 'rank':
        return rank_match(sig, RATIO, LIMIT)
    elif mode == 'fuzzy':
        return fuzzy_match(sig, LIMIT)
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
            debugp('rank match candidate: {} {}'.format(ratio, s))
            candidates.append(s)
    if not candidates:
        debugp('rank match no candidates, closest match: {}'.format(compares[0]))
        return candidates

    debugp('rank match: total={} limit={}'.format(len(candidates), limit))
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
    candidates = sort_songs(c_starts) + sort_songs(c_in)
    if not candidates:
        debugp('fuzzy match no candidates')
        return candidates
    debugp('fuzzy match: total={} limit={}'.format(len(candidates), limit))
    return limit_list(candidates, limit)

_key_lambda = lambda x: x['title']

def sort_songs(l):
    return sorted(l, key=_key_lambda)

def limit_list(l, limit):
    if len(l) > limit:
        return l[:limit]
    return l

# seems py3 will fail on this function if LC_ALL is not UTF-8,
# so running this script in subprocess must ensure all envs are inherited
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
    global LIMIT
    global RATIO
    LIMIT = int(LIMIT)
    RATIO = float(RATIO)

    # show envs
    if SHOW_ENVS:
        print('Env vars and default value')
        for i in global_keys:
            print('  BS_{:20}{}'.format(i, globals()[i]))
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

    debugp('global vars: MODE={} RATIO={} LIMIT={} FMT={}'.format(
        MODE, RATIO, LIMIT, FMT,
    ))
    # match songs
    try:
        matched = match_songs(query, MODE)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    if not matched:
        sys.exit(1)
    for s in matched:
        print(format_output_line(s))

songs = {
"baroriginal": {"album": "Anthology 2", "notes": "", "songwriters": "John Lennon\nPaul McCartney\nGeorge Harrison\nRingo Starr", "title": "12-Bar Original", "vocals": "Instrumental", "year": "1965"},
"adayinthelife": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "A Day in the Life", "vocals": "Lennon, McCartney", "year": "1967"},
"aharddaysnight": {"album": "UK: A Hard Day's Night US: 1962–1966", "notes": "", "songwriters": "Lennon\n(with McCartney)", "title": "A Hard Day's Night", "vocals": "Lennon, with McCartney", "year": "1964"},
"ashotofrhythmandblues": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Terry Thompson", "title": "A Shot of Rhythm and Blues", "vocals": "Lennon", "year": "1963"},
"atasteofhoney": {"album": "UK: Please Please Me US: The Early Beatles", "notes": "Cover", "songwriters": "Bobby Scott\nRic Marlow", "title": "A Taste of Honey", "vocals": "McCartney", "year": "1963"},
"acrosstheuniverse": {"album": "Let It Be", "notes": "", "songwriters": "Lennon", "title": "Across the Universe", "vocals": "Lennon", "year": "1968"},
"actnaturally": {"album": "UK: Help! US: Yesterday and Today", "notes": "Cover", "songwriters": "Johnny Russell\nVoni Morrison", "title": "Act Naturally", "vocals": "Starr", "year": "1965"},
"aintshesweet": {"album": "Anthology 1", "notes": "Cover", "songwriters": "Jack Yellen\nMilton Ager", "title": "Ain't She Sweet", "vocals": "Lennon", "year": "1961"},
"allivegottodo": {"album": "UK: With the Beatles US: Meet the Beatles!", "notes": "", "songwriters": "Lennon", "title": "All I've Got to Do", "vocals": "Lennon", "year": "1963"},
"allmyloving": {"album": "UK: With the Beatles US: Meet the Beatles!", "notes": "", "songwriters": "McCartney", "title": "All My Loving", "vocals": "McCartney", "year": "1963"},
"allthingsmustpass": {"album": "Anthology 3", "notes": "", "songwriters": "Harrison", "title": "All Things Must Pass", "vocals": "Harrison", "year": "1969"},
"alltogethernow": {"album": "Yellow Submarine", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "All Together Now", "vocals": "McCartney", "year": "1967"},
"allyouneedislove": {"album": "Magical Mystery Tour", "notes": "", "songwriters": "Lennon", "title": "All You Need Is Love", "vocals": "Lennon", "year": "1967"},
"andiloveher": {"album": "UK: A Hard Day's Night US: Something New", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "And I Love Her", "vocals": "McCartney", "year": "1964"},
"andyourbirdcansing": {"album": "UK: Revolver US: Yesterday and Today", "notes": "", "songwriters": "Lennon\n(with McCartney)", "title": "And Your Bird Can Sing", "vocals": "Lennon", "year": "1966"},
"annagotohim": {"album": "UK: Please Please Me US: The Early Beatles", "notes": "Cover", "songwriters": "Arthur Alexander", "title": "Anna (Go to Him)", "vocals": "Lennon", "year": "1963"},
"anothergirl": {"album": "Help!", "notes": "", "songwriters": "McCartney", "title": "Another Girl", "vocals": "McCartney", "year": "1965"},
"anytimeatall": {"album": "UK: A Hard Day's Night US: Something New", "notes": "", "songwriters": "Lennon\n(with McCartney)", "title": "Any Time at All", "vocals": "Lennon", "year": "1964"},
"askmewhy": {"album": "UK: Please Please Me US: The Early Beatles", "notes": "", "songwriters": "Lennon\n(with McCartney)", "title": "Ask Me Why", "vocals": "Lennon", "year": "1962"},
"babyitsyou": {"album": "UK: Please Please Me US: The Early Beatles", "notes": "Cover", "songwriters": "Burt Bacharach\nHal David\nLuther Dixon", "title": "Baby It's You", "vocals": "Lennon", "year": "1963"},
"babysinblack": {"album": "UK: Beatles for Sale US: Beatles '65", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "Baby's in Black", "vocals": "Lennon, McCartney", "year": "1964"},
"babyyourearichman": {"album": "Magical Mystery Tour", "notes": "Non-album single\nB-side of \"All You Need is Love\"", "songwriters": "Lennon\nMcCartney", "title": "Baby, You're a Rich Man", "vocals": "Lennon", "year": "1967"},
"backintheussr": {"album": "The Beatles", "notes": "", "songwriters": "McCartney", "title": "Back in the U.S.S.R.", "vocals": "McCartney", "year": "1968"},
"badboy": {"album": "UK: A Collection of Beatles Oldies US: Beatles VI", "notes": "Cover", "songwriters": "Larry Williams", "title": "Bad Boy", "vocals": "Lennon", "year": "1965"},
"badtome": {"album": "The Beatles Bootleg Recordings 1963", "notes": "Written for Billy J. Kramer", "songwriters": "Lennon", "title": "Bad to Me", "vocals": "Lennon", "year": "1963"},
"beautifuldreamer": {"album": "On Air – Live at the BBC Volume 2", "notes": "Cover", "songwriters": "Stephen Foster", "title": "Beautiful Dreamer", "vocals": "McCartney", "year": "1963"},
"because": {"album": "Abbey Road", "notes": "", "songwriters": "Lennon[25]", "title": "Because", "vocals": "Lennon, McCartney, Harrison", "year": "1969"},
"becauseiknowyoulovemeso": {"album": "Let It Be... Naked - Fly on the Wall bonus disc", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "Because I Know You Love Me So", "vocals": "Lennon, McCartney", "year": "1969"},
"beingforthebenefitofmrkite": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "notes": "", "songwriters": "Lennon", "title": "Being for the Benefit of Mr. Kite!", "vocals": "Lennon", "year": "1967"},
"birthday": {"album": "The Beatles", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "Birthday", "vocals": "McCartney, with Lennon", "year": "1968"},
"blackbird": {"album": "The Beatles", "notes": "", "songwriters": "McCartney", "title": "Blackbird", "vocals": "McCartney", "year": "1968"},
"bluejayway": {"album": "Magical Mystery Tour", "notes": "", "songwriters": "Harrison", "title": "Blue Jay Way", "vocals": "Harrison", "year": "1967"},
"boys": {"album": "UK: Please Please Me US: The Early Beatles", "notes": "Cover", "songwriters": "Luther Dixon\nWes Farrell", "title": "Boys", "vocals": "Starr", "year": "1963"},
"bésamemucho": {"album": "Anthology 1", "notes": "Cover", "songwriters": "Consuelo Velázquez\nSunny Skylar", "title": "Bésame Mucho", "vocals": "McCartney", "year": "1962"},
"cantbuymelove": {"album": "UK: A Hard Day's Night US: Hey Jude", "notes": "", "songwriters": "McCartney", "title": "Can't Buy Me Love", "vocals": "McCartney, with Lennon", "year": "1964"},
"carol": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Chuck Berry", "title": "Carol", "vocals": "Lennon", "year": "1963"},
"carrythatweight": {"album": "Abbey Road", "notes": "", "songwriters": "McCartney[32]", "title": "Carry That Weight", "vocals": "McCartney, with Lennon, Harrison, and Starr", "year": "1969"},
"catswalk": {"album": "N/A", "notes": "", "songwriters": "McCartney", "title": "Catswalk", "vocals": "N/A", "year": "1962"},
"cayenne": {"album": "Anthology 1", "notes": "", "songwriters": "McCartney", "title": "Cayenne", "vocals": "Instrumental", "year": "1960"},
"chains": {"album": "UK: Please Please Me US: The Early Beatles", "notes": "Cover", "songwriters": "Gerry Goffin\nCarole King", "title": "Chains", "vocals": "Harrison, (with Lennon, McCartney)", "year": "1963"},
"childofnature": {"album": "Let It Be... Naked - Fly on the Wall bonus disc", "notes": "Turned into Lennon's \"Jealous Guy\"", "songwriters": "Lennon", "title": "Child of Nature", "vocals": "Lennon", "year": "1968"},
"christmastimeishereagain": {"album": "The Beatles' Christmas Album", "notes": "Non-album single\nB-side of \"Free As A Bird\"", "songwriters": "Lennon\nMcCartney\nHarrison\nStarr", "title": "Christmas Time (Is Here Again)", "vocals": "Lennon, McCartney, Harrison, Starr", "year": "1967"},
"circles": {"album": "", "notes": "On Harrison's Gone Troppo", "songwriters": "Harrison", "title": "Circles", "vocals": "Harrison", "year": "1968"},
"clarabella": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Mike Pingitore", "title": "Clarabella", "vocals": "McCartney", "year": "1963"},
"cometogether": {"album": "Abbey Road", "notes": "Double A-side single with \"Something\"", "songwriters": "Lennon[33]", "title": "Come Together", "vocals": "Lennon", "year": "1969"},
"comeandgetit": {"album": "Anthology 3", "notes": "Recorded by Badfinger", "songwriters": "McCartney", "title": "Come and Get It", "vocals": "McCartney", "year": "1969"},
"crybabycry": {"album": "The Beatles", "notes": "", "songwriters": "Lennon", "title": "Cry Baby Cry", "vocals": "Lennon, with McCartney", "year": "1968"},
"cryforashadow": {"album": "Anthology 1", "notes": "", "songwriters": "Lennon and Harrison", "title": "Cry for a Shadow", "vocals": "Instrumental", "year": "1961"},
"cryingwaitinghoping": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Buddy Holly", "title": "Crying, Waiting, Hoping", "vocals": "Harrison", "year": "1963"},
"daytripper": {"album": "UK: A Collection of Beatles Oldies US: Yesterday and Today", "notes": "Double A-side with \"We Can Work It Out\"", "songwriters": "Lennon\n(with McCartney)", "title": "Day Tripper", "vocals": "Lennon, McCartney", "year": "1965"},
"dearprudence": {"album": "The Beatles", "notes": "McCartney on drums", "songwriters": "Lennon", "title": "Dear Prudence", "vocals": "Lennon", "year": "1968"},
"devilinherheart": {"album": "UK: With the Beatles US: The Beatles' Second Album", "notes": "Cover", "songwriters": "Drapkin (a.k.a. Ricky Dee)", "title": "Devil in Her Heart", "vocals": "Harrison", "year": "1963"},
"digit": {"album": "Let It Be", "notes": "", "songwriters": "Lennon\nMcCartney\nHarrison\nStarr", "title": "Dig It", "vocals": "Lennon", "year": "1969"},
"digapony": {"album": "Let It Be", "notes": "", "songwriters": "Lennon", "title": "Dig a Pony", "vocals": "Lennon", "year": "1969"},
"dizzymisslizzy": {"album": "UK: Help! US: Beatles VI", "notes": "Cover", "songwriters": "Larry Williams", "title": "Dizzy, Miss Lizzy", "vocals": "Lennon", "year": "1965"},
"doyouwanttoknowasecret": {"album": "UK: Please Please Me US: The Early Beatles", "notes": "", "songwriters": "Lennon", "title": "Do You Want to Know a Secret?", "vocals": "Harrison", "year": "1963"},
"doctorrobert": {"album": "UK: Revolver US: Yesterday and Today", "notes": "", "songwriters": "Lennon\n(with McCartney)", "title": "Doctor Robert", "vocals": "Lennon", "year": "1966"},
"dontbotherme": {"album": "UK: With the Beatles US: Meet the Beatles!", "notes": "", "songwriters": "Harrison", "title": "Don't Bother Me", "vocals": "Harrison", "year": "1963"},
"donteverchange": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Gerry Goffin\nCarole King", "title": "Don't Ever Change", "vocals": "Harrison and McCartney", "year": "1963"},
"dontletmedown": {"album": "UK: 1967–1970 US: Hey Jude", "notes": "Non-album single\nB-side of \"Get Back\"", "songwriters": "Lennon", "title": "Don't Let Me Down", "vocals": "Lennon (with McCartney)", "year": "1969"},
"dontpassmeby": {"album": "The Beatles", "notes": "", "songwriters": "Starkey[b]", "title": "Don't Pass Me By", "vocals": "Starr", "year": "1968"},
"drivemycar": {"album": "UK: Rubber Soul US: Yesterday and Today", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "Drive My Car", "vocals": "McCartney, with Lennon", "year": "1965"},
"eightdaysaweek": {"album": "UK: Beatles for Sale US: Beatles VI", "notes": "US single only", "songwriters": "McCartney\n(with Lennon)", "title": "Eight Days a Week", "vocals": "Lennon, with McCartney", "year": "1964"},
"eleanorrigby": {"album": "Revolver", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "Eleanor Rigby", "vocals": "McCartney", "year": "1966"},
"etcetera": {"album": "Unreleased", "notes": "", "songwriters": "McCartney", "title": "Etcetera", "vocals": "McCartney", "year": "1968"},
"everylittlething": {"album": "UK: Beatles for Sale US: Beatles VI", "notes": "", "songwriters": "McCartney", "title": "Every Little Thing", "vocals": "Lennon, with McCartney", "year": "1964"},
"everybodysgotsomethingtohideexceptmeandmymonkey": {"album": "The Beatles", "notes": "", "songwriters": "Lennon", "title": "Everybody's Got Something to Hide Except Me and My Monkey", "vocals": "Lennon", "year": "1968"},
"everybodystryingtobemybaby": {"album": "UK: Beatles for Sale US: Beatles '65", "notes": "Cover", "songwriters": "Carl Perkins", "title": "Everybody's Trying to Be My Baby", "vocals": "Harrison", "year": "1964"},
"fancymychanceswithyou": {"album": "Let It Be... Naked - Fly on the Wall bonus disc", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "Fancy My Chances with You", "vocals": "Lennon, McCartney", "year": "1969"},
"fixingahole": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "notes": "", "songwriters": "McCartney", "title": "Fixing a Hole", "vocals": "McCartney", "year": "1967"},
"flying": {"album": "Magical Mystery Tour", "notes": "", "songwriters": "Lennon\nMcCartney\nHarrison\nStarr", "title": "Flying", "vocals": "Instrumental", "year": "1967"},
"fornoone": {"album": "Revolver", "notes": "Featuring Alan Civil on French horn", "songwriters": "McCartney", "title": "For No One", "vocals": "McCartney", "year": "1966"},
"foryoublue": {"album": "Let It Be", "notes": "", "songwriters": "Harrison", "title": "For You Blue", "vocals": "Harrison", "year": "1969"},
"freeasabird": {"album": "Anthology 1", "notes": "", "songwriters": "Lennon\nMcCartney\nHarrison\nStarr", "title": "Free as a Bird", "vocals": "Lennon, McCartney and Harrison", "year": "1977"},
"frommetoyou": {"album": "UK: A Collection of Beatles Oldies US: 1962–1966", "notes": "Non-album single", "songwriters": "Lennon\nMcCartney", "title": "From Me to You", "vocals": "Lennon, McCartney", "year": "1963"},
"fromustoyou": {"album": "Live at the BBC", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "From Us to You", "vocals": "Lennon, McCartney", "year": "1963"},
"getback": {"album": "Let It Be", "notes": "", "songwriters": "McCartney", "title": "Get Back", "vocals": "McCartney", "year": "1969"},
"gettingbetter": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "Getting Better", "vocals": "McCartney, with Lennon", "year": "1967"},
"girl": {"album": "Rubber Soul", "notes": "", "songwriters": "Lennon", "title": "Girl", "vocals": "Lennon", "year": "1965"},
"gladallover": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Roy C. Bennett\nSid Tepper\nAaron Schroeder", "title": "Glad All Over", "vocals": "Harrison", "year": "1963"},
"glassonion": {"album": "The Beatles", "notes": "", "songwriters": "Lennon", "title": "Glass Onion", "vocals": "Lennon", "year": "1968"},
"goldenslumbers": {"album": "Abbey Road", "notes": "", "songwriters": "McCartney[32]", "title": "Golden Slumbers", "vocals": "McCartney", "year": "1969"},
"gooddaysunshine": {"album": "Revolver", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "Good Day Sunshine", "vocals": "McCartney", "year": "1966"},
"goodmorninggoodmorning": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "notes": "McCartney plays guitar solo", "songwriters": "Lennon", "title": "Good Morning Good Morning", "vocals": "Lennon", "year": "1967"},
"goodnight": {"album": "The Beatles", "notes": "", "songwriters": "Lennon", "title": "Good Night", "vocals": "Starr", "year": "1968"},
"goodbye": {"album": "", "notes": "", "songwriters": "McCartney", "title": "Goodbye", "vocals": "McCartney", "year": "1969"},
"gottogetyouintomylife": {"album": "Revolver", "notes": "", "songwriters": "McCartney", "title": "Got to Get You into My Life", "vocals": "McCartney", "year": "1966"},
"hallelujahiloveherso": {"album": "Anthology 1", "notes": "Cover", "songwriters": "Ray Charles", "title": "Hallelujah, I Love Her So", "vocals": "McCartney", "year": "1960"},
"happinessisawarmgun": {"album": "The Beatles", "notes": "", "songwriters": "Lennon", "title": "Happiness Is a Warm Gun", "vocals": "Lennon", "year": "1968"},
"heather": {"album": "", "notes": "Donovan plays on the demo", "songwriters": "McCartney", "title": "Heather", "vocals": "McCartney", "year": "1968"},
"hellolittlegirl": {"album": "Anthology 1", "notes": "Recorded by The Fourmost\nreleased August 1963", "songwriters": "Lennon", "title": "Hello Little Girl", "vocals": "Lennon", "year": "1962"},
"hellogoodbye": {"album": "Magical Mystery Tour", "notes": "", "songwriters": "McCartney", "title": "Hello, Goodbye", "vocals": "McCartney", "year": "1967"},
"help": {"album": "Help!", "notes": "", "songwriters": "Lennon\n(with McCartney)", "title": "Help!", "vocals": "Lennon", "year": "1965"},
"helterskelter": {"album": "The Beatles", "notes": "Featuring Starr with shouted words in stereo version", "songwriters": "McCartney", "title": "Helter Skelter", "vocals": "McCartney", "year": "1968"},
"hermajesty": {"album": "Abbey Road", "notes": "", "songwriters": "McCartney", "title": "Her Majesty", "vocals": "McCartney", "year": "1969"},
"herecomesthesun": {"album": "Abbey Road", "notes": "", "songwriters": "Harrison", "title": "Here Comes the Sun", "vocals": "Harrison", "year": "1969"},
"herethereandeverywhere": {"album": "Revolver", "notes": "", "songwriters": "McCartney", "title": "Here, There and Everywhere", "vocals": "McCartney", "year": "1966"},
"heybulldog": {"album": "Yellow Submarine", "notes": "", "songwriters": "Lennon", "title": "Hey Bulldog", "vocals": "Lennon, with McCartney", "year": "1968"},
"heyjude": {"album": "UK: 1967–1970 US: Hey Jude", "notes": "", "songwriters": "McCartney", "title": "Hey Jude", "vocals": "McCartney", "year": "1968"},
"hippyhippyshake": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Chan Romero", "title": "Hippy Hippy Shake", "vocals": "McCartney", "year": "1963"},
"holdmetight": {"album": "UK: With the Beatles US: Meet the Beatles!", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "Hold Me Tight", "vocals": "McCartney", "year": "1963"},
"honeydont": {"album": "UK: Beatles for Sale US: Beatles '65", "notes": "Cover", "songwriters": "Carl Perkins", "title": "Honey Don't", "vocals": "Starr", "year": "1964"},
"honeypie": {"album": "The Beatles", "notes": "", "songwriters": "McCartney", "title": "Honey Pie", "vocals": "McCartney", "year": "1968"},
"howdoyoudoit": {"album": "Anthology 1", "notes": "Cover", "songwriters": "Mitch Murray", "title": "How Do You Do It?", "vocals": "Lennon", "year": "1962"},
"iamthewalrus": {"album": "Magical Mystery Tour", "notes": "", "songwriters": "Lennon", "title": "I Am the Walrus", "vocals": "Lennon", "year": "1967"},
"icallyourname": {"album": "UK: \"Long Tall Sally\" EP US: The Beatles' Second Album", "notes": "First release by Billy J Kramer with the Dakotas\n(July 1963)", "songwriters": "Lennon", "title": "I Call Your Name", "vocals": "Lennon", "year": "1964"},
"idontwanttospoiltheparty": {"album": "UK: Beatles for Sale US: Beatles VI", "notes": "", "songwriters": "Lennon", "title": "I Don't Want to Spoil the Party", "vocals": "Lennon, with McCartney", "year": "1964"},
"ifeelfine": {"album": "UK: A Collection of Beatles Oldies US: Beatles '65", "notes": "Non-album single", "songwriters": "Lennon", "title": "I Feel Fine", "vocals": "Lennon", "year": "1964"},
"iforgottoremembertoforget": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Stan Kesler and Charlie Feathers", "title": "I Forgot to Remember to Forget", "vocals": "Harrison", "year": "1964"},
"igotawoman": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Ray Charles", "title": "I Got a Woman", "vocals": "Lennon", "year": "1963"},
"igottofindmybaby": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Chuck Berry", "title": "I Got to Find My Baby", "vocals": "Lennon", "year": "1963"},
"ijustdontunderstand": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Marijohn Wilkin\nKent Westberry", "title": "I Just Don't Understand", "vocals": "Lennon", "year": "1963"},
"ilostmylittlegirl": {"album": "", "notes": "", "songwriters": "McCartney", "title": "I Lost My Little Girl", "vocals": "Lennon", "year": "1962"},
"imemine": {"album": "Let It Be", "notes": "", "songwriters": "Harrison", "title": "I Me Mine", "vocals": "Harrison", "year": "1970"},
"ineedyou": {"album": "Help!", "notes": "", "songwriters": "Harrison", "title": "I Need You", "vocals": "Harrison", "year": "1965"},
"isawherstandingthere": {"album": "UK: Please Please Me US: Meet the Beatles!", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "I Saw Her Standing There", "vocals": "McCartney, with Lennon", "year": "1963"},
"ishouldhaveknownbetter": {"album": "UK: A Hard Day's Night US: Hey Jude", "notes": "", "songwriters": "Lennon", "title": "I Should Have Known Better", "vocals": "Lennon", "year": "1964"},
"iwannabeyourman": {"album": "UK: With the Beatles US: Meet the Beatles!", "notes": "Written for the Rolling Stones", "songwriters": "McCartney\n(with Lennon)", "title": "I Wanna Be Your Man", "vocals": "Starr", "year": "1963"},
"iwantyoushessoheavy": {"album": "Abbey Road", "notes": "", "songwriters": "Lennon", "title": "I Want You (She's So Heavy)", "vocals": "Lennon", "year": "1969"},
"iwanttoholdyourhand": {"album": "UK: A Collection of Beatles Oldies US: Meet the Beatles!", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "I Want to Hold Your Hand", "vocals": "Lennon, McCartney", "year": "1963"},
"iwanttotellyou": {"album": "Revolver", "notes": "", "songwriters": "Harrison", "title": "I Want to Tell You", "vocals": "Harrison", "year": "1966"},
"iwill": {"album": "The Beatles", "notes": "", "songwriters": "McCartney", "title": "I Will", "vocals": "McCartney", "year": "1968"},
"illbeback": {"album": "UK: A Hard Day's Night US: Beatles '65", "notes": "", "songwriters": "Lennon", "title": "I'll Be Back", "vocals": "Lennon and McCartney)", "year": "1964"},
"illbeonmyway": {"album": "Live at the BBC", "notes": "Single by Billy J Kramer with the Dakotas\n(April 1963)", "songwriters": "McCartney", "title": "I'll Be on My Way", "vocals": "Lennon", "year": "1963"},
"illcryinstead": {"album": "UK: A Hard Day's Night US: Something New", "notes": "", "songwriters": "Lennon", "title": "I'll Cry Instead", "vocals": "Lennon", "year": "1964"},
"illfollowthesun": {"album": "UK: Beatles for Sale US: Beatles '65", "notes": "", "songwriters": "McCartney", "title": "I'll Follow the Sun", "vocals": "McCartney, with Lennon", "year": "1964"},
"illgetyou": {"album": "UK: Past Masters Volume 1 US: The Beatles' Second Album", "notes": "Non-album single\nB-side of \"She Loves You\"", "songwriters": "Lennon\nMcCartney", "title": "I'll Get You", "vocals": "Lennon, with McCartney", "year": "1963"},
"imdown": {"album": "Rock 'n' Roll Music", "notes": "Non-album single\nB-side of \"Help!\"", "songwriters": "McCartney", "title": "I'm Down", "vocals": "McCartney", "year": "1965"},
"imgonnasitrightdownandcryoveryou": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Joe Thomas\nHoward Biggs", "title": "I'm Gonna Sit Right Down and Cry (Over You)", "vocals": "Lennon", "year": "1963"},
"imhappyjusttodancewithyou": {"album": "UK: A Hard Day's Night US: Something New", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "I'm Happy Just to Dance with You", "vocals": "Harrison", "year": "1964"},
"iminlove": {"album": "The Beatles Bootleg Recordings 1963", "notes": "Written for The Fourmost\n(single released November 1963)", "songwriters": "Lennon", "title": "I'm In Love", "vocals": "Lennon", "year": "1963"},
"imlookingthroughyou": {"album": "Rubber Soul", "notes": "", "songwriters": "McCartney", "title": "I'm Looking Through You", "vocals": "McCartney, with Lennon", "year": "1965"},
"imonlysleeping": {"album": "UK: Revolver US: Yesterday and Today", "notes": "", "songwriters": "Lennon", "title": "I'm Only Sleeping", "vocals": "Lennon", "year": "1966"},
"imsotired": {"album": "The Beatles", "notes": "", "songwriters": "Lennon", "title": "I'm So Tired", "vocals": "Lennon", "year": "1968"},
"imtalkingaboutyou": {"album": "Live! at the Star-Club in Hamburg, Germany; 1962", "notes": "Cover", "songwriters": "Chuck Berry", "title": "I'm Talking About You", "vocals": "Lennon", "year": "1962"},
"imaloser": {"album": "UK: Beatles for Sale US: Beatles '65", "notes": "", "songwriters": "Lennon", "title": "I'm a Loser", "vocals": "Lennon", "year": "1964"},
"ivegotafeeling": {"album": "Let It Be", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "I've Got a Feeling", "vocals": "McCartney, with Lennon", "year": "1969"},
"ivejustseenaface": {"album": "UK: Help! US: Rubber Soul", "notes": "", "songwriters": "McCartney", "title": "I've Just Seen a Face", "vocals": "McCartney", "year": "1965"},
"ififell": {"album": "UK: A Hard Day's Night US: Something New", "notes": "", "songwriters": "Lennon", "title": "If I Fell", "vocals": "Lennon, with McCartney", "year": "1964"},
"ifineededsomeone": {"album": "UK: Rubber Soul US: Yesterday and Today", "notes": "", "songwriters": "Harrison", "title": "If I Needed Someone", "vocals": "Harrison", "year": "1965"},
"ifyouvegottrouble": {"album": "Anthology 2", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "If You've Got Trouble", "vocals": "Starr", "year": "1965"},
"inmylife": {"album": "Rubber Soul", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "In My Life", "vocals": "Lennon", "year": "1965"},
"inspiteofallthedanger": {"album": "Anthology 1", "notes": "", "songwriters": "McCartney and Harrison", "title": "In Spite of All the Danger", "vocals": "Lennon", "year": "1958"},
"itwontbelong": {"album": "UK: With the Beatles US: Meet the Beatles!", "notes": "", "songwriters": "Lennon\n(with McCartney)", "title": "It Won't Be Long", "vocals": "Lennon", "year": "1963"},
"itsalltoomuch": {"album": "Yellow Submarine", "notes": "", "songwriters": "Harrison", "title": "It's All Too Much", "vocals": "Harrison", "year": "1967"},
"itsonlylove": {"album": "UK: Help! US: Rubber Soul", "notes": "", "songwriters": "Lennon", "title": "It's Only Love", "vocals": "Lennon", "year": "1965"},
"jazzpianosong": {"album": "Let it Be film", "notes": "", "songwriters": "McCartney\nStarr", "title": "Jazz Piano Song", "vocals": "McCartney", "year": "1969"},
"jessiesdream": {"album": "Magical Mystery Tour", "notes": "", "songwriters": "Lennon, McCartney, Harrison, Starr", "title": "Jessie's Dream", "vocals": "Instrumental", "year": "1967"},
"johnnybgoode": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Chuck Berry", "title": "Johnny B. Goode", "vocals": "Lennon", "year": "1964"},
"julia": {"album": "The Beatles", "notes": "", "songwriters": "Lennon", "title": "Julia", "vocals": "Lennon", "year": "1968"},
"junk": {"album": "Anthology 3", "notes": "", "songwriters": "McCartney", "title": "Junk", "vocals": "McCartney", "year": "1968"},
"kansascityheyheyheyhey": {"album": "UK: Beatles for Sale US: Beatles VI", "notes": "Cover", "songwriters": "Jerry Leiber and Mike Stoller/Little Richard", "title": "Kansas City/Hey-Hey-Hey-Hey!", "vocals": "McCartney", "year": "1964"},
"keepyourhandsoffmybaby": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Gerry Goffin\nCarole King", "title": "Keep Your Hands Off My Baby", "vocals": "Lennon", "year": "1963"},
"kommgibmirdeinehand": {"album": "UK: Rarities US: Something New", "notes": "Non-album single\nGerman version of \"I Want to Hold Your Hand\"", "songwriters": "Lennon\nMcCartney\nJean Nicolas\nHeinz Hellmer", "title": "Komm, gib mir deine Hand", "vocals": "Lennon, McCartney", "year": "1964"},
"ladymadonna": {"album": "UK: 1967-1970 US: Hey Jude", "notes": "Non-album single", "songwriters": "McCartney\n(with Lennon)", "title": "Lady Madonna", "vocals": "McCartney", "year": "1968"},
"leavemykittenalone": {"album": "Anthology 1", "notes": "Cover", "songwriters": "Little Willie John\nTitus Turner\nJames McDougall", "title": "Leave My Kitten Alone", "vocals": "Lennon", "year": "1964"},
"lendmeyourcomb": {"album": "Anthology 1", "notes": "Cover", "songwriters": "Kay Twomey\nFred Wise\nBen Weisman", "title": "Lend Me Your Comb", "vocals": "Lennon, McCartney", "year": "1963"},
"letitbe": {"album": "Let It Be", "notes": "", "songwriters": "McCartney", "title": "Let It Be", "vocals": "McCartney", "year": "1969"},
"likedreamersdo": {"album": "Anthology 1", "notes": "Recorded by The Applejacks", "songwriters": "McCartney", "title": "Like Dreamers Do", "vocals": "McCartney", "year": "1962"},
"littlechild": {"album": "UK: With the Beatles US: Meet the Beatles!", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "Little Child", "vocals": "Lennon, McCartney", "year": "1963"},
"lonesometearsinmyeyes": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Johnny Burnette\nDorsey Burnette\nPaul Burlison\nAl Mortimer", "title": "Lonesome Tears in My Eyes", "vocals": "Lennon", "year": "1963"},
"longtallsally": {"album": "UK: Long Tall Sally EP US: The Beatles' Second Album", "notes": "Non-album single\nCover", "songwriters": "Robert \"Bumps\" Blackwell\nEnotris Johnson\nLittle Richard", "title": "Long Tall Sally", "vocals": "McCartney", "year": "1964"},
"longlonglong": {"album": "The Beatles", "notes": "", "songwriters": "Harrison", "title": "Long, Long, Long", "vocals": "Harrison", "year": "1968"},
"lookingglass": {"album": "", "notes": "", "songwriters": "McCartney", "title": "Looking Glass", "vocals": "McCartney", "year": "1962"},
"lovemedo": {"album": "UK: Please Please Me US: The Early Beatles", "notes": "featuring Andy White on drums", "songwriters": "McCartney\n(with Lennon)", "title": "Love Me Do", "vocals": "McCartney, with Lennon", "year": "1962"},
"loveyouto": {"album": "Revolver", "notes": "", "songwriters": "Harrison", "title": "Love You To", "vocals": "Harrison", "year": "1966"},
"loveoftheloved": {"album": "", "notes": "Single by Cilla Black\n(September 1963)", "songwriters": "McCartney\n(with Lennon)", "title": "Love of the Loved", "vocals": "McCartney", "year": "1962"},
"lovelyrita": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "notes": "", "songwriters": "McCartney", "title": "Lovely Rita", "vocals": "McCartney", "year": "1967"},
"lucille": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Little Richard\nAlbert Collins", "title": "Lucille", "vocals": "McCartney", "year": "1963"},
"lucyintheskywithdiamonds": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "notes": "", "songwriters": "Lennon", "title": "Lucy in the Sky with Diamonds", "vocals": "Lennon", "year": "1967"},
"madman": {"album": "N/A", "notes": "From Get Back/Let It Be sessions", "songwriters": "Lennon", "title": "Madman", "vocals": "Lennon", "year": "1969"},
"maggiemae": {"album": "Let It Be", "notes": "Cover", "songwriters": "Traditional, arr. Lennon, McCartney\nHarrison, Starr", "title": "Maggie Mae", "vocals": "Lennon, with McCartney", "year": "1969"},
"magicalmysterytour": {"album": "Magical Mystery Tour", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "Magical Mystery Tour", "vocals": "McCartney, with Lennon", "year": "1967"},
"mailmanbringmenomoreblues": {"album": "Anthology 3", "notes": "Cover", "songwriters": "Ruth Roberts\nBill Katz\nStanley Clayton", "title": "Mailman, Bring Me No More Blues", "vocals": "Lennon", "year": "1969"},
"marthamydear": {"album": "The Beatles", "notes": "", "songwriters": "McCartney", "title": "Martha My Dear", "vocals": "McCartney", "year": "1968"},
"matchbox": {"album": "UK: \"Long Tall Sally\" EP US: Something New", "notes": "Cover", "songwriters": "Carl Perkins\nBlind Lemon Jefferson", "title": "Matchbox", "vocals": "Starr", "year": "1964"},
"maxwellssilverhammer": {"album": "Abbey Road", "notes": "", "songwriters": "McCartney[56]", "title": "Maxwell's Silver Hammer", "vocals": "McCartney", "year": "1969"},
"meanmrmustard": {"album": "Abbey Road", "notes": "", "songwriters": "Lennon[58]", "title": "Mean Mr. Mustard", "vocals": "Lennon, with McCartney", "year": "1969"},
"memphistennessee": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Chuck Berry", "title": "Memphis, Tennessee", "vocals": "Lennon", "year": "1963"},
"michelle": {"album": "Rubber Soul", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "Michelle", "vocals": "McCartney", "year": "1965"},
"misery": {"album": "UK: Please Please Me US: Introducing… The Beatles", "notes": "", "songwriters": "Lennon\n(with McCartney)", "title": "Misery", "vocals": "Lennon and McCartney", "year": "1963"},
"moneythatswhatiwant": {"album": "UK: With the Beatles US: The Beatles Second Album", "notes": "Cover", "songwriters": "Berry Gordy\nJanie Bradford", "title": "Money (That's What I Want)", "vocals": "Lennon", "year": "1963"},
"moonlightbay": {"album": "Anthology 1", "notes": "Performed on the Morecambe and Wise Show in 2/12/63", "songwriters": "Percy Wenrich\nEdward Madden", "title": "Moonlight Bay", "vocals": "Lennon, McCartney, Harrison, Eric Morecambe, Ernie Wise", "year": "1963"},
"mothernaturesson": {"album": "The Beatles", "notes": "", "songwriters": "McCartney", "title": "Mother Nature's Son", "vocals": "McCartney", "year": "1968"},
"mrmoonlight": {"album": "UK: Beatles for Sale US: Beatles '65", "notes": "Cover", "songwriters": "Roy Lee Johnson", "title": "Mr. Moonlight", "vocals": "Lennon", "year": "1964"},
"noreply": {"album": "UK: Beatles for Sale US: Beatles '65", "notes": "", "songwriters": "Lennon\n(with McCartney)", "title": "No Reply", "vocals": "Lennon, with McCartney", "year": "1964"},
"norwegianwoodthisbirdhasflown": {"album": "Rubber Soul", "notes": "", "songwriters": "Lennon\n(with McCartney)", "title": "Norwegian Wood (This Bird Has Flown)", "vocals": "Lennon", "year": "1965"},
"notguilty": {"album": "Anthology 3", "notes": "", "songwriters": "Harrison", "title": "Not Guilty", "vocals": "Harrison", "year": "1968"},
"notasecondtime": {"album": "UK: With the Beatles US: Meet the Beatles!", "notes": "", "songwriters": "Lennon", "title": "Not a Second Time", "vocals": "Lennon", "year": "1963"},
"nothinshakinbuttheleavesonthetrees": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Eddie Fontaine", "title": "Nothin' Shakin' (But the Leaves on the Trees)", "vocals": "Harrison", "year": "1963"},
"nowhereman": {"album": "UK: Rubber Soul US: Yesterday and Today", "notes": "", "songwriters": "Lennon\n(with McCartney)", "title": "Nowhere Man", "vocals": "Lennon, with McCartney and Harrison", "year": "1965"},
"obladioblada": {"album": "The Beatles", "notes": "", "songwriters": "McCartney", "title": "Ob-La-Di, Ob-La-Da", "vocals": "McCartney", "year": "1968"},
"octopussgarden": {"album": "Abbey Road", "notes": "", "songwriters": "Starkey[c]", "title": "Octopus's Garden", "vocals": "Starr", "year": "1969"},
"ohdarling": {"album": "Abbey Road", "notes": "", "songwriters": "McCartney[32]", "title": "Oh! Darling", "vocals": "McCartney", "year": "1969"},
"oldbrownshoe": {"album": "UK: 1967–1970 US: Hey Jude", "notes": "Non-album single\nB-side of \"The Ballad of John and Yoko\"", "songwriters": "Harrison", "title": "Old Brown Shoe", "vocals": "Harrison", "year": "1969"},
"oneafter": {"album": "Let It Be", "notes": "", "songwriters": "Lennon", "title": "One After 909", "vocals": "Lennon, with McCartney", "year": "1969"},
"oneandoneistwo": {"album": "", "notes": "Single by The Strangers with Mike Shannon\n(May 1964)", "songwriters": "McCartney", "title": "One and One Is Two", "vocals": "McCartney", "year": "1964"},
"onlyanorthernsong": {"album": "Yellow Submarine", "notes": "", "songwriters": "Harrison", "title": "Only a Northern Song", "vocals": "Harrison", "year": "1967"},
"oohmysoul": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Little Richard", "title": "Ooh! My Soul", "vocals": "McCartney", "year": "1963"},
"psiloveyou": {"album": "UK: Please Please Me US: The Early Beatles", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "P.S. I Love You", "vocals": "McCartney", "year": "1962"},
"paperbackwriter": {"album": "UK: A Collection of Beatles Oldies US: Hey Jude", "notes": "Non-album single", "songwriters": "McCartney", "title": "Paperback Writer", "vocals": "McCartney", "year": "1966"},
"pennylane": {"album": "Magical Mystery Tour", "notes": "Double A-side single\nwith \"Strawberry Fields Forever\"", "songwriters": "McCartney", "title": "Penny Lane", "vocals": "McCartney", "year": "1966"},
"piggies": {"album": "The Beatles", "notes": "", "songwriters": "Harrison", "title": "Piggies", "vocals": "Harrison", "year": "1968"},
"pleasemrpostman": {"album": "UK: With the Beatles US: The Beatles' Second Album", "notes": "Cover", "songwriters": "Georgia Dobbins\nWilliam Garrett\nBrian Holland\nRobert Bateman\nFreddie Gorman", "title": "Please Mr. Postman", "vocals": "Lennon", "year": "1963"},
"pleasepleaseme": {"album": "UK: Please Please Me US: The Early Beatles", "notes": "Single", "songwriters": "Lennon", "title": "Please Please Me", "vocals": "Lennon and McCartney", "year": "1962"},
"polythenepam": {"album": "Abbey Road", "notes": "", "songwriters": "Lennon", "title": "Polythene Pam", "vocals": "Lennon", "year": "1969"},
"rain": {"album": "UK: Rarities US: Hey Jude", "notes": "Non-album single\nB-side to \"Paperback Writer\"", "songwriters": "Lennon", "title": "Rain", "vocals": "Lennon", "year": "1966"},
"reallove": {"album": "Anthology 2", "notes": "", "songwriters": "Lennon", "title": "Real Love", "vocals": "Lennon", "year": "1980"},
"revolution": {"album": "UK: 1967-1970 US: Hey Jude", "notes": "Non-album single\nB-side to \"Hey Jude\"", "songwriters": "Lennon", "title": "Revolution", "vocals": "Lennon", "year": "1968"},
"revolution": {"album": "The Beatles", "notes": "", "songwriters": "Lennon", "title": "Revolution 1", "vocals": "Lennon", "year": "1968"},
"revolution": {"album": "The Beatles", "notes": "", "songwriters": "Lennon\n(with Ono and Harrison)", "title": "Revolution 9", "vocals": "Sound Collage", "year": "1968"},
"ripitupshakerattleandrollbluesuedeshoes": {"album": "Anthology 3", "notes": "Cover", "songwriters": "Robert Blackwell, John Marascalco (\"Rip It Up\")\nCharles Calhoun(\"Shake, Rattle, and Roll\")\nCarl Perkins (\"Blue Suede Shoes\")", "title": "Rip It Up / Shake, Rattle, and Roll / Blue Suede Shoes", "vocals": "Lennon, McCartney", "year": "1969"},
"rockandrollmusic": {"album": "UK: Beatles for Sale US: Beatles '65", "notes": "Cover", "songwriters": "Chuck Berry", "title": "Rock and Roll Music", "vocals": "Lennon", "year": "1964"},
"rockyraccoon": {"album": "The Beatles", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "Rocky Raccoon", "vocals": "McCartney", "year": "1968"},
"rolloverbeethoven": {"album": "UK: With the Beatles US: The Beatles' Second Album", "notes": "Cover", "songwriters": "Chuck Berry", "title": "Roll Over Beethoven", "vocals": "Harrison", "year": "1963"},
"runforyourlife": {"album": "Rubber Soul", "notes": "", "songwriters": "Lennon\n(with McCartney)", "title": "Run for Your Life", "vocals": "Lennon", "year": "1965"},
"savoytruffle": {"album": "The Beatles", "notes": "", "songwriters": "Harrison", "title": "Savoy Truffle", "vocals": "Harrison", "year": "1968"},
"searchin": {"album": "Anthology 1", "notes": "Cover", "songwriters": "Jerry Leiber and Mike Stoller", "title": "Searchin'", "vocals": "McCartney", "year": "1962"},
"septemberintherain": {"album": "", "notes": "Cover", "songwriters": "Al Dubin\nHarry Warren", "title": "September in the Rain", "vocals": "McCartney", "year": "1962"},
"sexysadie": {"album": "The Beatles", "notes": "", "songwriters": "Lennon", "title": "Sexy Sadie", "vocals": "Lennon", "year": "1968"},
"sgtpepperslonelyheartsclubband": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "notes": "", "songwriters": "McCartney", "title": "Sgt. Pepper's Lonely Hearts Club Band", "vocals": "McCartney, with Lennon, Harrison and Starr", "year": "1967"},
"sgtpepperslonelyheartsclubbandreprise": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "notes": "", "songwriters": "McCartney", "title": "Sgt. Pepper's Lonely Hearts Club Band (Reprise)", "vocals": "McCartney, Lennon, Harrison, Starr", "year": "1967"},
"shakininthesixties": {"album": "Unreleased", "notes": "", "songwriters": "Lennon", "title": "Shakin' in the Sixties", "vocals": "Lennon", "year": "1969"},
"shecameinthroughthebathroomwindow": {"album": "Abbey Road", "notes": "", "songwriters": "McCartney", "title": "She Came in Through the Bathroom Window", "vocals": "McCartney", "year": "1969"},
"shelovesyou": {"album": "UK: A Collection of Beatles Oldies US: The Beatles Second Album", "notes": "Non-album single", "songwriters": "Lennon\nMcCartney", "title": "She Loves You", "vocals": "Lennon, McCartney", "year": "1963"},
"shesaidshesaid": {"album": "Revolver", "notes": "", "songwriters": "Lennon", "title": "She Said She Said", "vocals": "Lennon", "year": "1966"},
"shesleavinghome": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "She's Leaving Home", "vocals": "McCartney, with Lennon", "year": "1967"},
"shesawoman": {"album": "UK: Rarities US: Beatles '65", "notes": "Non-album single\nB-side to \"I Feel Fine\"", "songwriters": "McCartney\n(with Lennon)", "title": "She's a Woman", "vocals": "McCartney", "year": "1964"},
"shout": {"album": "Anthology 1", "notes": "Cover", "songwriters": "Rudolph Isley\nRonald Isley\nO'Kelly Isley Jr.", "title": "Shout", "vocals": "Lennon, McCartney, Harrison, Starr", "year": "1964"},
"sieliebtdich": {"album": "UK: Rarities US: Rarities", "notes": "Non-album single\nGerman version of \"She Loves You\"", "songwriters": "Lennon\nMcCartney\nJean Nicolas\nLee Montogue", "title": "Sie liebt dich", "vocals": "Lennon, McCartney", "year": "1964"},
"slowdown": {"album": "UK: \"Long Tall Sally\" EP US: Something New", "notes": "Non-album single\nB-side of \"Matchbox\"\nCover", "songwriters": "Larry Williams", "title": "Slow Down", "vocals": "Lennon", "year": "1964"},
"sohowcomenoonelovesme": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Felice and Boudleaux Bryant", "title": "So How Come (No One Loves Me)", "vocals": "Harrison", "year": "1963"},
"soldieroflovelaydownyourarms": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Buzz Cason\nTony Moon", "title": "Soldier of Love (Lay Down Your Arms)", "vocals": "Lennon", "year": "1963"},
"someotherguy": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Jerry Leiber and Mike Stoller\nRichie Barrett", "title": "Some Other Guy", "vocals": "Lennon, McCartney", "year": "1963"},
"something": {"album": "Abbey Road", "notes": "Double A-side single\nwith \"Come Together\"", "songwriters": "Harrison", "title": "Something", "vocals": "Harrison", "year": "1969"},
"sourmilksea": {"album": "Unreleased", "notes": "White Album\"\" outtake", "songwriters": "Harrison", "title": "Sour Milk Sea", "vocals": "Harrison", "year": "1968"},
"stepinsidelovelosparanoias": {"album": "Anthology 3", "notes": "\"Step Inside Love\" was recorded by Cilla Black\n(1968)", "songwriters": "McCartney (\"Step Inside Love\")\nLennon–McCartney\nHarrison–Starr (\"Los Paranoias\")", "title": "Step Inside Love/Los Paranoias", "vocals": "McCartney", "year": "1968"},
"strawberryfieldsforever": {"album": "Magical Mystery Tour", "notes": "Double A-side single\n(with \"Penny Lane\")", "songwriters": "Lennon", "title": "Strawberry Fields Forever", "vocals": "Lennon", "year": "1966"},
"sunking": {"album": "Abbey Road", "notes": "", "songwriters": "Lennon", "title": "Sun King", "vocals": "Lennon, with McCartney and Harrison", "year": "1969"},
"suretofallinlovewithyou": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Carl Perkins\nQuinton Claunch\nBill Cantrell", "title": "Sure to Fall (in Love with You)", "vocals": "McCartney", "year": "1963"},
"sweetlittlesixteen": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Chuck Berry", "title": "Sweet Little Sixteen", "vocals": "Lennon", "year": "1963"},
"takegoodcareofmybaby": {"album": "", "notes": "Cover", "songwriters": "Gerry Goffin\nCarole King", "title": "Take Good Care of My Baby", "vocals": "Harrison", "year": "1962"},
"takingatriptocarolina": {"album": "Let It Be... Naked - Fly on the Wall bonus disc", "notes": "", "songwriters": "Starr", "title": "Taking a Trip to Carolina", "vocals": "Starr", "year": "1969"},
"taxman": {"album": "Revolver", "notes": "McCartney plays guitar solo", "songwriters": "Harrison", "title": "Taxman", "vocals": "Harrison, with Lennon and McCartney", "year": "1966"},
"teddyboy": {"album": "Anthology 3", "notes": "\"Let It Be\" outtake", "songwriters": "McCartney", "title": "Teddy Boy", "vocals": "McCartney", "year": "1969"},
"tellmewhatyousee": {"album": "UK: Help! US: Beatles VI", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "Tell Me What You See", "vocals": "McCartney, with Lennon", "year": "1965"},
"tellmewhy": {"album": "UK: A Hard Day's Night US: Something New", "notes": "", "songwriters": "Lennon", "title": "Tell Me Why", "vocals": "Lennon", "year": "1964"},
"thankyougirl": {"album": "UK: Rarities US: The Beatles Second Album", "notes": "Non-album single\nB-side of \"From Me To You\"", "songwriters": "Lennon\nMcCartney", "title": "Thank You Girl", "vocals": "Lennon, McCartney", "year": "1963"},
"thatmeansalot": {"album": "Anthology 2", "notes": "Recorded by P.J. Proby\n(1965)", "songwriters": "McCartney", "title": "That Means a Lot", "vocals": "McCartney", "year": "1965"},
"thatllbetheday": {"album": "Anthology 1", "notes": "Cover", "songwriters": "Jerry Allison\nBuddy Holly\nNorman Petty", "title": "That'll Be the Day", "vocals": "Lennon", "year": "1958"},
"thatsallrightmama": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Arthur Crudup", "title": "That’s All Right (Mama)", "vocals": "McCartney", "year": "1963"},
"theballadofjohnandyoko": {"album": "UK: 1967–1970 US: Hey Jude", "notes": "", "songwriters": "Lennon", "title": "The Ballad of John and Yoko", "vocals": "Lennon, with McCartney", "year": "1969"},
"thecontinuingstoryofbungalowbill": {"album": "The Beatles", "notes": "", "songwriters": "Lennon", "title": "The Continuing Story of Bungalow Bill", "vocals": "Lennon", "year": "1968"},
"theend": {"album": "Abbey Road", "notes": "", "songwriters": "McCartney", "title": "The End", "vocals": "McCartney", "year": "1969"},
"thefoolonthehill": {"album": "Magical Mystery Tour", "notes": "", "songwriters": "McCartney", "title": "The Fool on the Hill", "vocals": "McCartney", "year": "1967"},
"thehoneymoonsong": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Mikis Theodorakis\nSansom", "title": "The Honeymoon Song", "vocals": "McCartney", "year": "1963"},
"theinnerlight": {"album": "UK: Rarities US: Rarities", "notes": "Non-album single\nB-side of \"Lady Madonna\"", "songwriters": "Harrison", "title": "The Inner Light", "vocals": "Harrison", "year": "1968"},
"thelongandwindingroad": {"album": "Let It Be", "notes": "", "songwriters": "McCartney", "title": "The Long and Winding Road", "vocals": "McCartney", "year": "1969"},
"thenightbefore": {"album": "Help!", "notes": "", "songwriters": "McCartney", "title": "The Night Before", "vocals": "McCartney", "year": "1965"},
"thesheikofaraby": {"album": "Anthology 1", "notes": "Cover", "songwriters": "Harry B. Smith\nFrancis Wheeler\nTed Snyder", "title": "The Sheik of Araby", "vocals": "Harrison", "year": "1962"},
"theword": {"album": "Rubber Soul", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "The Word", "vocals": "Lennon, with McCartney and Harrison", "year": "1965"},
"theresaplace": {"album": "UK: Please Please Me US: Rarities", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "There's a Place", "vocals": "Lennon, McCartney", "year": "1963"},
"thingswesaidtoday": {"album": "UK: A Hard Day's Night US: Something New", "notes": "", "songwriters": "McCartney", "title": "Things We Said Today", "vocals": "McCartney", "year": "1964"},
"thinkforyourself": {"album": "Rubber Soul", "notes": "", "songwriters": "Harrison", "title": "Think for Yourself", "vocals": "Harrison", "year": "1965"},
"thisboy": {"album": "UK: Rarities US: Meet the Beatles!", "notes": "Non-album single\nB-side of \"I Want To Hold Your Hand\"", "songwriters": "Lennon", "title": "This Boy", "vocals": "Lennon, with McCartney and Harrison", "year": "1963"},
"threecoolcats": {"album": "Anthology 1", "notes": "Cover", "songwriters": "Jerry Leiber and Mike Stoller", "title": "Three Cool Cats", "vocals": "Harrison", "year": "1962"},
"tickettoride": {"album": "Help!", "notes": "", "songwriters": "Lennon", "title": "Ticket to Ride", "vocals": "Lennon, with McCartney", "year": "1965"},
"tilltherewasyou": {"album": "UK: With the Beatles US: Meet the Beatles!", "notes": "Cover", "songwriters": "Meredith Willson", "title": "Till There Was You", "vocals": "McCartney", "year": "1963"},
"tipofmytongue": {"album": "Unreleased", "notes": "Recorded by Tommy Quickly\n(Released in 1963)", "songwriters": "Lennon\nMcCartney", "title": "Tip of My Tongue", "vocals": "Lennon, McCartney", "year": ""},
"toknowheristoloveher": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Phil Spector", "title": "To Know Her is to Love Her", "vocals": "Lennon", "year": "1963"},
"tomorrowneverknows": {"album": "Revolver", "notes": "", "songwriters": "Lennon", "title": "Tomorrow Never Knows", "vocals": "Lennon", "year": "1966"},
"toomuchmonkeybusiness": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Chuck Berry", "title": "Too Much Monkey Business", "vocals": "Lennon", "year": "1963"},
"twistandshout": {"album": "UK: Please Please Me US: The Early Beatles", "notes": "Cover", "songwriters": "Phil Medley\nBert Berns", "title": "Twist and Shout", "vocals": "Lennon", "year": "1963"},
"twoofus": {"album": "Let It Be", "notes": "", "songwriters": "McCartney", "title": "Two of Us", "vocals": "McCartney, with Lennon", "year": "1969"},
"wait": {"album": "Rubber Soul", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "Wait", "vocals": "McCartney and Lennon", "year": "1965"},
"watchingrainbows": {"album": "", "notes": "", "songwriters": "Lennon\nand McCartney", "title": "Watching Rainbows", "vocals": "Lennon", "year": "1969"},
"wecanworkitout": {"album": "UK: A Collection of Beatles Oldies US: Yesterday and Today", "notes": "Non-album single\nDouble A-side with \"Day Tripper\"", "songwriters": "McCartney\n(with Lennon)", "title": "We Can Work It Out", "vocals": "McCartney, with Lennon", "year": "1965"},
"whatgoeson": {"album": "UK: Rubber Soul US: Yesterday and Today", "notes": "", "songwriters": "Lennon\nMcCartney\nStarkey[d]", "title": "What Goes On", "vocals": "Starr", "year": "1965"},
"whatyouredoing": {"album": "UK: Beatles for Sale US: Beatles VI", "notes": "", "songwriters": "McCartney", "title": "What You're Doing", "vocals": "McCartney", "year": "1964"},
"whatsthenewmaryjane": {"album": "Anthology 3", "notes": "\"White Album\" outtake", "songwriters": "Lennon", "title": "What's The New Mary Jane", "vocals": "Lennon", "year": "1968"},
"whenigethome": {"album": "UK: A Hard Day's Night US: Something New", "notes": "", "songwriters": "Lennon", "title": "When I Get Home", "vocals": "Lennon", "year": "1964"},
"whenimsixtyfour": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "notes": "", "songwriters": "McCartney", "title": "When I'm Sixty-Four", "vocals": "McCartney", "year": "1966"},
"whilemyguitargentlyweeps": {"album": "The Beatles", "notes": "Eric Clapton plays lead guitar\n(uncredited)", "songwriters": "Harrison", "title": "While My Guitar Gently Weeps", "vocals": "Harrison", "year": "1968"},
"whydontwedoitintheroad": {"album": "The Beatles", "notes": "", "songwriters": "McCartney", "title": "Why Don't We Do It in the Road?", "vocals": "McCartney", "year": "1968"},
"wildhoneypie": {"album": "The Beatles", "notes": "", "songwriters": "McCartney", "title": "Wild Honey Pie", "vocals": "McCartney", "year": "1968"},
"withalittlehelpfrommyfriends": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "With a Little Help from My Friends", "vocals": "Starr, with Lennon and McCartney", "year": "1967"},
"withinyouwithoutyou": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "notes": "", "songwriters": "Lennon", "title": "Within You Without You", "vocals": "Lennon", "year": "1967"},
"woman": {"album": "Let It Be film", "notes": "Single by Peter and Gordon\n(January 1966)", "songwriters": "McCartney (as Bernard Webb)", "title": "Woman", "vocals": "McCartney", "year": "1965"},
"wordsoflove": {"album": "UK: Beatles for Sale US: Beatles VI", "notes": "Cover", "songwriters": "Buddy Holly", "title": "Words of Love", "vocals": "Lennon, McCartney", "year": "1964"},
"yellowsubmarine": {"album": "Revolver", "notes": "", "songwriters": "McCartney\n(with Lennon)", "title": "Yellow Submarine", "vocals": "Starr", "year": "1966"},
"yerblues": {"album": "The Beatles", "notes": "", "songwriters": "Lennon", "title": "Yer Blues", "vocals": "Lennon", "year": "1968"},
"yesitis": {"album": "UK: Rarities US: Beatles VI", "notes": "Non-album single\nB-side of \"Ticket to Ride\"", "songwriters": "Lennon", "title": "Yes It Is", "vocals": "Lennon, McCartney and Harrison", "year": "1965"},
"yesterday": {"album": "UK: Help! US: Yesterday and Today", "notes": "", "songwriters": "McCartney", "title": "Yesterday", "vocals": "McCartney", "year": "1965"},
"youcantdothat": {"album": "UK: A Hard Day's Night US: The Beatles Second Album", "notes": "", "songwriters": "Lennon", "title": "You Can't Do That", "vocals": "Lennon", "year": "1964"},
"youknowmynamelookupthenumber": {"album": "UK: Rarities US: Rarities", "notes": "Non-album single\nB-side of \"Let It Be\"", "songwriters": "Lennon\n(with McCartney)", "title": "You Know My Name (Look Up the Number)", "vocals": "Lennon, McCartney", "year": "1967"},
"youknowwhattodo": {"album": "Anthology 1", "notes": "", "songwriters": "Harrison", "title": "You Know What to Do", "vocals": "Harrison", "year": "1964"},
"youlikemetoomuch": {"album": "UK: Help! US: Beatles VI", "notes": "", "songwriters": "Harrison", "title": "You Like Me Too Much", "vocals": "Harrison", "year": "1965"},
"younevergivemeyourmoney": {"album": "Abbey Road", "notes": "", "songwriters": "McCartney[61]", "title": "You Never Give Me Your Money", "vocals": "McCartney", "year": "1969"},
"youwontseeme": {"album": "Rubber Soul", "notes": "", "songwriters": "McCartney", "title": "You Won't See Me", "vocals": "McCartney", "year": "1965"},
"youllbemine": {"album": "Anthology 1", "notes": "", "songwriters": "Lennon\nMcCartney", "title": "You'll Be Mine", "vocals": "McCartney", "year": "1960"},
"youregoingtolosethatgirl": {"album": "Help!", "notes": "", "songwriters": "Lennon", "title": "You're Going to Lose That Girl", "vocals": "Lennon", "year": "1965"},
"youvegottohideyourloveaway": {"album": "Help!", "notes": "", "songwriters": "Lennon", "title": "You've Got to Hide Your Love Away", "vocals": "Lennon", "year": "1965"},
"youvereallygotaholdonme": {"album": "UK: With the Beatles US: The Beatles Second Album", "notes": "Cover", "songwriters": "Smokey Robinson", "title": "You've Really Got a Hold on Me", "vocals": "Lennon and Harrison", "year": "1963"},
"youngblood": {"album": "Live at the BBC", "notes": "Cover", "songwriters": "Jerry Leiber and Mike Stoller", "title": "Young Blood", "vocals": "Harrison", "year": "1963"},
"yourmothershouldknow": {"album": "Magical Mystery Tour", "notes": "", "songwriters": "McCartney", "title": "Your Mother Should Know", "vocals": "McCartney", "year": "1967"},
}

if __name__ == '__main__':
    main()
