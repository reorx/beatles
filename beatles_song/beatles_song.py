#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
from difflib import SequenceMatcher

__version__ = '0.1.0'

DEBUG = False
PURGE_QUERY = False
MATCH_MODE = 'rank'  # rank, fuzzy, or mixed
MATCH_LIMIT = 1
MATCH_RATIO = 0.75
FMT = '{title} - {vocals}, {year}'
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
    debugp('query={} sig={}'.format(repr(query), sig))

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
    candidates = c_starts + c_in
    if not candidates:
        debugp('fuzzy match no candidates')
        return candidates
    debugp('fuzzy match: total={} limit={}'.format(len(candidates), limit))
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
            print('  BS_{}	{}'.format(i, globals()[i]))
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

    debugp('global vars: MATCH_MODE={} MATCH_RATIO={} MATCH_LIMIT={} FMT={}'.format(
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

songs = {
"baroriginal": {"album": "Anthology 2", "title": "12-Bar Original", "notes": "", "vocals": "Instrumental", "year": "1965", "songwriters": "John Lennon\nPaul McCartney\nGeorge Harrison\nRingo Starr"},
"adayinthelife": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "title": "A Day in the Life", "notes": "", "vocals": "Lennon, McCartney", "year": "1967", "songwriters": "Lennon\nMcCartney"},
"aharddaysnight": {"album": "UK: A Hard Day's Night US: 1962–1966", "title": "A Hard Day's Night", "notes": "", "vocals": "Lennon, with McCartney", "year": "1964", "songwriters": "Lennon\n(with McCartney)"},
"ashotofrhythmandblues": {"album": "Live at the BBC", "title": "A Shot of Rhythm and Blues", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Terry Thompson"},
"atasteofhoney": {"album": "UK: Please Please Me US: The Early Beatles", "title": "A Taste of Honey", "notes": "Cover", "vocals": "McCartney", "year": "1963", "songwriters": "Bobby Scott\nRic Marlow"},
"acrosstheuniverse": {"album": "Let It Be", "title": "Across the Universe", "notes": "", "vocals": "Lennon", "year": "1968", "songwriters": "Lennon"},
"actnaturally": {"album": "UK: Help! US: Yesterday and Today", "title": "Act Naturally", "notes": "Cover", "vocals": "Starr", "year": "1965", "songwriters": "Johnny Russell\nVoni Morrison"},
"aintshesweet": {"album": "Anthology 1", "title": "Ain't She Sweet", "notes": "Cover", "vocals": "Lennon", "year": "1961", "songwriters": "Jack Yellen\nMilton Ager"},
"allivegottodo": {"album": "UK: With the Beatles US: Meet the Beatles!", "title": "All I've Got to Do", "notes": "", "vocals": "Lennon", "year": "1963", "songwriters": "Lennon"},
"allmyloving": {"album": "UK: With the Beatles US: Meet the Beatles!", "title": "All My Loving", "notes": "", "vocals": "McCartney", "year": "1963", "songwriters": "McCartney"},
"allthingsmustpass": {"album": "Anthology 3", "title": "All Things Must Pass", "notes": "", "vocals": "Harrison", "year": "1969", "songwriters": "Harrison"},
"alltogethernow": {"album": "Yellow Submarine", "title": "All Together Now", "notes": "", "vocals": "McCartney", "year": "1967", "songwriters": "McCartney\n(with Lennon)"},
"allyouneedislove": {"album": "Magical Mystery Tour", "title": "All You Need Is Love", "notes": "", "vocals": "Lennon", "year": "1967", "songwriters": "Lennon"},
"andiloveher": {"album": "UK: A Hard Day's Night US: Something New", "title": "And I Love Her", "notes": "", "vocals": "McCartney", "year": "1964", "songwriters": "McCartney\n(with Lennon)"},
"andyourbirdcansing": {"album": "UK: Revolver US: Yesterday and Today", "title": "And Your Bird Can Sing", "notes": "", "vocals": "Lennon", "year": "1966", "songwriters": "Lennon\n(with McCartney)"},
"annagotohim": {"album": "UK: Please Please Me US: The Early Beatles", "title": "Anna (Go to Him)", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Arthur Alexander"},
"anothergirl": {"album": "Help!", "title": "Another Girl", "notes": "", "vocals": "McCartney", "year": "1965", "songwriters": "McCartney"},
"anytimeatall": {"album": "UK: A Hard Day's Night US: Something New", "title": "Any Time at All", "notes": "", "vocals": "Lennon", "year": "1964", "songwriters": "Lennon\n(with McCartney)"},
"askmewhy": {"album": "UK: Please Please Me US: The Early Beatles", "title": "Ask Me Why", "notes": "", "vocals": "Lennon", "year": "1962", "songwriters": "Lennon\n(with McCartney)"},
"babyitsyou": {"album": "UK: Please Please Me US: The Early Beatles", "title": "Baby It's You", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Burt Bacharach\nHal David\nLuther Dixon"},
"babysinblack": {"album": "UK: Beatles for Sale US: Beatles '65", "title": "Baby's in Black", "notes": "", "vocals": "Lennon, McCartney", "year": "1964", "songwriters": "Lennon\nMcCartney"},
"babyyourearichman": {"album": "Magical Mystery Tour", "title": "Baby, You're a Rich Man", "notes": "Non-album single\nB-side of \"All You Need is Love\"", "vocals": "Lennon", "year": "1967", "songwriters": "Lennon\nMcCartney"},
"backintheussr": {"album": "The Beatles", "title": "Back in the U.S.S.R.", "notes": "", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney"},
"badboy": {"album": "UK: A Collection of Beatles Oldies US: Beatles VI", "title": "Bad Boy", "notes": "Cover", "vocals": "Lennon", "year": "1965", "songwriters": "Larry Williams"},
"badtome": {"album": "The Beatles Bootleg Recordings 1963", "title": "Bad to Me", "notes": "Written for Billy J. Kramer", "vocals": "Lennon", "year": "1963", "songwriters": "Lennon"},
"beautifuldreamer": {"album": "On Air – Live at the BBC Volume 2", "title": "Beautiful Dreamer", "notes": "Cover", "vocals": "McCartney", "year": "1963", "songwriters": "Stephen Foster"},
"because": {"album": "Abbey Road", "title": "Because", "notes": "", "vocals": "Lennon, McCartney, Harrison", "year": "1969", "songwriters": "Lennon[25]"},
"becauseiknowyoulovemeso": {"album": "Let It Be... Naked - Fly on the Wall bonus disc", "title": "Because I Know You Love Me So", "notes": "", "vocals": "Lennon, McCartney", "year": "1969", "songwriters": "Lennon\nMcCartney"},
"beingforthebenefitofmrkite": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "title": "Being for the Benefit of Mr. Kite!", "notes": "", "vocals": "Lennon", "year": "1967", "songwriters": "Lennon"},
"birthday": {"album": "The Beatles", "title": "Birthday", "notes": "", "vocals": "McCartney, with Lennon", "year": "1968", "songwriters": "Lennon\nMcCartney"},
"blackbird": {"album": "The Beatles", "title": "Blackbird", "notes": "", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney"},
"bluejayway": {"album": "Magical Mystery Tour", "title": "Blue Jay Way", "notes": "", "vocals": "Harrison", "year": "1967", "songwriters": "Harrison"},
"boys": {"album": "UK: Please Please Me US: The Early Beatles", "title": "Boys", "notes": "Cover", "vocals": "Starr", "year": "1963", "songwriters": "Luther Dixon\nWes Farrell"},
"bsamemucho": {"album": "Anthology 1", "title": "Bésame Mucho", "notes": "Cover", "vocals": "McCartney", "year": "1962", "songwriters": "Consuelo Velázquez\nSunny Skylar"},
"cantbuymelove": {"album": "UK: A Hard Day's Night US: Hey Jude", "title": "Can't Buy Me Love", "notes": "", "vocals": "McCartney, with Lennon", "year": "1964", "songwriters": "McCartney"},
"carol": {"album": "Live at the BBC", "title": "Carol", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Chuck Berry"},
"carrythatweight": {"album": "Abbey Road", "title": "Carry That Weight", "notes": "", "vocals": "McCartney, with Lennon, Harrison, and Starr", "year": "1969", "songwriters": "McCartney[32]"},
"catswalk": {"album": "N/A", "title": "Catswalk", "notes": "", "vocals": "N/A", "year": "1962", "songwriters": "McCartney"},
"cayenne": {"album": "Anthology 1", "title": "Cayenne", "notes": "", "vocals": "Instrumental", "year": "1960", "songwriters": "McCartney"},
"chains": {"album": "UK: Please Please Me US: The Early Beatles", "title": "Chains", "notes": "Cover", "vocals": "Harrison, (with Lennon, McCartney)", "year": "1963", "songwriters": "Gerry Goffin\nCarole King"},
"childofnature": {"album": "Let It Be... Naked - Fly on the Wall bonus disc", "title": "Child of Nature", "notes": "Turned into Lennon's \"Jealous Guy\"", "vocals": "Lennon", "year": "1968", "songwriters": "Lennon"},
"christmastimeishereagain": {"album": "The Beatles' Christmas Album", "title": "Christmas Time (Is Here Again)", "notes": "Non-album single\nB-side of \"Free As A Bird\"", "vocals": "Lennon, McCartney, Harrison, Starr", "year": "1967", "songwriters": "Lennon\nMcCartney\nHarrison\nStarr"},
"circles": {"album": "", "title": "Circles", "notes": "On Harrison's Gone Troppo", "vocals": "Harrison", "year": "1968", "songwriters": "Harrison"},
"clarabella": {"album": "Live at the BBC", "title": "Clarabella", "notes": "Cover", "vocals": "McCartney", "year": "1963", "songwriters": "Mike Pingitore"},
"cometogether": {"album": "Abbey Road", "title": "Come Together", "notes": "Double A-side single with \"Something\"", "vocals": "Lennon", "year": "1969", "songwriters": "Lennon[33]"},
"comeandgetit": {"album": "Anthology 3", "title": "Come and Get It", "notes": "Recorded by Badfinger", "vocals": "McCartney", "year": "1969", "songwriters": "McCartney"},
"crybabycry": {"album": "The Beatles", "title": "Cry Baby Cry", "notes": "", "vocals": "Lennon, with McCartney", "year": "1968", "songwriters": "Lennon"},
"cryforashadow": {"album": "Anthology 1", "title": "Cry for a Shadow", "notes": "", "vocals": "Instrumental", "year": "1961", "songwriters": "Lennon and Harrison"},
"cryingwaitinghoping": {"album": "Live at the BBC", "title": "Crying, Waiting, Hoping", "notes": "Cover", "vocals": "Harrison", "year": "1963", "songwriters": "Buddy Holly"},
"daytripper": {"album": "UK: A Collection of Beatles Oldies US: Yesterday and Today", "title": "Day Tripper", "notes": "Double A-side with \"We Can Work It Out\"", "vocals": "Lennon, McCartney", "year": "1965", "songwriters": "Lennon\n(with McCartney)"},
"dearprudence": {"album": "The Beatles", "title": "Dear Prudence", "notes": "McCartney on drums", "vocals": "Lennon", "year": "1968", "songwriters": "Lennon"},
"devilinherheart": {"album": "UK: With the Beatles US: The Beatles' Second Album", "title": "Devil in Her Heart", "notes": "Cover", "vocals": "Harrison", "year": "1963", "songwriters": "Drapkin (a.k.a. Ricky Dee)"},
"digit": {"album": "Let It Be", "title": "Dig It", "notes": "", "vocals": "Lennon", "year": "1969", "songwriters": "Lennon\nMcCartney\nHarrison\nStarr"},
"digapony": {"album": "Let It Be", "title": "Dig a Pony", "notes": "", "vocals": "Lennon", "year": "1969", "songwriters": "Lennon"},
"dizzymisslizzy": {"album": "UK: Help! US: Beatles VI", "title": "Dizzy, Miss Lizzy", "notes": "Cover", "vocals": "Lennon", "year": "1965", "songwriters": "Larry Williams"},
"doyouwanttoknowasecret": {"album": "UK: Please Please Me US: The Early Beatles", "title": "Do You Want to Know a Secret?", "notes": "", "vocals": "Harrison", "year": "1963", "songwriters": "Lennon"},
"doctorrobert": {"album": "UK: Revolver US: Yesterday and Today", "title": "Doctor Robert", "notes": "", "vocals": "Lennon", "year": "1966", "songwriters": "Lennon\n(with McCartney)"},
"dontbotherme": {"album": "UK: With the Beatles US: Meet the Beatles!", "title": "Don't Bother Me", "notes": "", "vocals": "Harrison", "year": "1963", "songwriters": "Harrison"},
"donteverchange": {"album": "Live at the BBC", "title": "Don't Ever Change", "notes": "Cover", "vocals": "Harrison and McCartney", "year": "1963", "songwriters": "Gerry Goffin\nCarole King"},
"dontletmedown": {"album": "UK: 1967–1970 US: Hey Jude", "title": "Don't Let Me Down", "notes": "Non-album single\nB-side of \"Get Back\"", "vocals": "Lennon (with McCartney)", "year": "1969", "songwriters": "Lennon"},
"dontpassmeby": {"album": "The Beatles", "title": "Don't Pass Me By", "notes": "", "vocals": "Starr", "year": "1968", "songwriters": "Starkey[b]"},
"drivemycar": {"album": "UK: Rubber Soul US: Yesterday and Today", "title": "Drive My Car", "notes": "", "vocals": "McCartney, with Lennon", "year": "1965", "songwriters": "McCartney\n(with Lennon)"},
"eightdaysaweek": {"album": "UK: Beatles for Sale US: Beatles VI", "title": "Eight Days a Week", "notes": "US single only", "vocals": "Lennon, with McCartney", "year": "1964", "songwriters": "McCartney\n(with Lennon)"},
"eleanorrigby": {"album": "Revolver", "title": "Eleanor Rigby", "notes": "", "vocals": "McCartney", "year": "1966", "songwriters": "McCartney\n(with Lennon)"},
"etcetera": {"album": "Unreleased", "title": "Etcetera", "notes": "", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney"},
"everylittlething": {"album": "UK: Beatles for Sale US: Beatles VI", "title": "Every Little Thing", "notes": "", "vocals": "Lennon, with McCartney", "year": "1964", "songwriters": "McCartney"},
"everybodysgotsomethingtohideexceptmeandmymonkey": {"album": "The Beatles", "title": "Everybody's Got Something to Hide Except Me and My Monkey", "notes": "", "vocals": "Lennon", "year": "1968", "songwriters": "Lennon"},
"everybodystryingtobemybaby": {"album": "UK: Beatles for Sale US: Beatles '65", "title": "Everybody's Trying to Be My Baby", "notes": "Cover", "vocals": "Harrison", "year": "1964", "songwriters": "Carl Perkins"},
"fancymychanceswithyou": {"album": "Let It Be... Naked - Fly on the Wall bonus disc", "title": "Fancy My Chances with You", "notes": "", "vocals": "Lennon, McCartney", "year": "1969", "songwriters": "Lennon\nMcCartney"},
"fixingahole": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "title": "Fixing a Hole", "notes": "", "vocals": "McCartney", "year": "1967", "songwriters": "McCartney"},
"flying": {"album": "Magical Mystery Tour", "title": "Flying", "notes": "", "vocals": "Instrumental", "year": "1967", "songwriters": "Lennon\nMcCartney\nHarrison\nStarr"},
"fornoone": {"album": "Revolver", "title": "For No One", "notes": "Featuring Alan Civil on French horn", "vocals": "McCartney", "year": "1966", "songwriters": "McCartney"},
"foryoublue": {"album": "Let It Be", "title": "For You Blue", "notes": "", "vocals": "Harrison", "year": "1969", "songwriters": "Harrison"},
"freeasabird": {"album": "Anthology 1", "title": "Free as a Bird", "notes": "", "vocals": "Lennon, McCartney and Harrison", "year": "1977", "songwriters": "Lennon\nMcCartney\nHarrison\nStarr"},
"frommetoyou": {"album": "UK: A Collection of Beatles Oldies US: 1962–1966", "title": "From Me to You", "notes": "Non-album single", "vocals": "Lennon, McCartney", "year": "1963", "songwriters": "Lennon\nMcCartney"},
"fromustoyou": {"album": "Live at the BBC", "title": "From Us to You", "notes": "", "vocals": "Lennon, McCartney", "year": "1963", "songwriters": "Lennon\nMcCartney"},
"getback": {"album": "Let It Be", "title": "Get Back", "notes": "", "vocals": "McCartney", "year": "1969", "songwriters": "McCartney"},
"gettingbetter": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "title": "Getting Better", "notes": "", "vocals": "McCartney, with Lennon", "year": "1967", "songwriters": "McCartney\n(with Lennon)"},
"girl": {"album": "Rubber Soul", "title": "Girl", "notes": "", "vocals": "Lennon", "year": "1965", "songwriters": "Lennon"},
"gladallover": {"album": "Live at the BBC", "title": "Glad All Over", "notes": "Cover", "vocals": "Harrison", "year": "1963", "songwriters": "Roy C. Bennett\nSid Tepper\nAaron Schroeder"},
"glassonion": {"album": "The Beatles", "title": "Glass Onion", "notes": "", "vocals": "Lennon", "year": "1968", "songwriters": "Lennon"},
"goldenslumbers": {"album": "Abbey Road", "title": "Golden Slumbers", "notes": "", "vocals": "McCartney", "year": "1969", "songwriters": "McCartney[32]"},
"gooddaysunshine": {"album": "Revolver", "title": "Good Day Sunshine", "notes": "", "vocals": "McCartney", "year": "1966", "songwriters": "McCartney\n(with Lennon)"},
"goodmorninggoodmorning": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "title": "Good Morning Good Morning", "notes": "McCartney plays guitar solo", "vocals": "Lennon", "year": "1967", "songwriters": "Lennon"},
"goodnight": {"album": "The Beatles", "title": "Good Night", "notes": "", "vocals": "Starr", "year": "1968", "songwriters": "Lennon"},
"goodbye": {"album": "", "title": "Goodbye", "notes": "", "vocals": "McCartney", "year": "1969", "songwriters": "McCartney"},
"gottogetyouintomylife": {"album": "Revolver", "title": "Got to Get You into My Life", "notes": "", "vocals": "McCartney", "year": "1966", "songwriters": "McCartney"},
"hallelujahiloveherso": {"album": "Anthology 1", "title": "Hallelujah, I Love Her So", "notes": "Cover", "vocals": "McCartney", "year": "1960", "songwriters": "Ray Charles"},
"happinessisawarmgun": {"album": "The Beatles", "title": "Happiness Is a Warm Gun", "notes": "", "vocals": "Lennon", "year": "1968", "songwriters": "Lennon"},
"heather": {"album": "", "title": "Heather", "notes": "Donovan plays on the demo", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney"},
"hellolittlegirl": {"album": "Anthology 1", "title": "Hello Little Girl", "notes": "Recorded by The Fourmost\nreleased August 1963", "vocals": "Lennon", "year": "1962", "songwriters": "Lennon"},
"hellogoodbye": {"album": "Magical Mystery Tour", "title": "Hello, Goodbye", "notes": "", "vocals": "McCartney", "year": "1967", "songwriters": "McCartney"},
"help": {"album": "Help!", "title": "Help!", "notes": "", "vocals": "Lennon", "year": "1965", "songwriters": "Lennon\n(with McCartney)"},
"helterskelter": {"album": "The Beatles", "title": "Helter Skelter", "notes": "Featuring Starr with shouted words in stereo version", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney"},
"hermajesty": {"album": "Abbey Road", "title": "Her Majesty", "notes": "", "vocals": "McCartney", "year": "1969", "songwriters": "McCartney"},
"herecomesthesun": {"album": "Abbey Road", "title": "Here Comes the Sun", "notes": "", "vocals": "Harrison", "year": "1969", "songwriters": "Harrison"},
"herethereandeverywhere": {"album": "Revolver", "title": "Here, There and Everywhere", "notes": "", "vocals": "McCartney", "year": "1966", "songwriters": "McCartney"},
"heybulldog": {"album": "Yellow Submarine", "title": "Hey Bulldog", "notes": "", "vocals": "Lennon, with McCartney", "year": "1968", "songwriters": "Lennon"},
"heyjude": {"album": "UK: 1967–1970 US: Hey Jude", "title": "Hey Jude", "notes": "", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney"},
"hippyhippyshake": {"album": "Live at the BBC", "title": "Hippy Hippy Shake", "notes": "Cover", "vocals": "McCartney", "year": "1963", "songwriters": "Chan Romero"},
"holdmetight": {"album": "UK: With the Beatles US: Meet the Beatles!", "title": "Hold Me Tight", "notes": "", "vocals": "McCartney", "year": "1963", "songwriters": "McCartney\n(with Lennon)"},
"honeydont": {"album": "UK: Beatles for Sale US: Beatles '65", "title": "Honey Don't", "notes": "Cover", "vocals": "Starr", "year": "1964", "songwriters": "Carl Perkins"},
"honeypie": {"album": "The Beatles", "title": "Honey Pie", "notes": "", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney"},
"howdoyoudoit": {"album": "Anthology 1", "title": "How Do You Do It?", "notes": "Cover", "vocals": "Lennon", "year": "1962", "songwriters": "Mitch Murray"},
"iamthewalrus": {"album": "Magical Mystery Tour", "title": "I Am the Walrus", "notes": "", "vocals": "Lennon", "year": "1967", "songwriters": "Lennon"},
"icallyourname": {"album": "UK: \"Long Tall Sally\" EP US: The Beatles' Second Album", "title": "I Call Your Name", "notes": "First release by Billy J Kramer with the Dakotas\n(July 1963)", "vocals": "Lennon", "year": "1964", "songwriters": "Lennon"},
"idontwanttospoiltheparty": {"album": "UK: Beatles for Sale US: Beatles VI", "title": "I Don't Want to Spoil the Party", "notes": "", "vocals": "Lennon, with McCartney", "year": "1964", "songwriters": "Lennon"},
"ifeelfine": {"album": "UK: A Collection of Beatles Oldies US: Beatles '65", "title": "I Feel Fine", "notes": "Non-album single", "vocals": "Lennon", "year": "1964", "songwriters": "Lennon"},
"iforgottoremembertoforget": {"album": "Live at the BBC", "title": "I Forgot to Remember to Forget", "notes": "Cover", "vocals": "Harrison", "year": "1964", "songwriters": "Stan Kesler and Charlie Feathers"},
"igotawoman": {"album": "Live at the BBC", "title": "I Got a Woman", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Ray Charles"},
"igottofindmybaby": {"album": "Live at the BBC", "title": "I Got to Find My Baby", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Chuck Berry"},
"ijustdontunderstand": {"album": "Live at the BBC", "title": "I Just Don't Understand", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Marijohn Wilkin\nKent Westberry"},
"ilostmylittlegirl": {"album": "", "title": "I Lost My Little Girl", "notes": "", "vocals": "Lennon", "year": "1962", "songwriters": "McCartney"},
"imemine": {"album": "Let It Be", "title": "I Me Mine", "notes": "", "vocals": "Harrison", "year": "1970", "songwriters": "Harrison"},
"ineedyou": {"album": "Help!", "title": "I Need You", "notes": "", "vocals": "Harrison", "year": "1965", "songwriters": "Harrison"},
"isawherstandingthere": {"album": "UK: Please Please Me US: Meet the Beatles!", "title": "I Saw Her Standing There", "notes": "", "vocals": "McCartney, with Lennon", "year": "1963", "songwriters": "McCartney\n(with Lennon)"},
"ishouldhaveknownbetter": {"album": "UK: A Hard Day's Night US: Hey Jude", "title": "I Should Have Known Better", "notes": "", "vocals": "Lennon", "year": "1964", "songwriters": "Lennon"},
"iwannabeyourman": {"album": "UK: With the Beatles US: Meet the Beatles!", "title": "I Wanna Be Your Man", "notes": "Written for the Rolling Stones", "vocals": "Starr", "year": "1963", "songwriters": "McCartney\n(with Lennon)"},
"iwantyoushessoheavy": {"album": "Abbey Road", "title": "I Want You (She's So Heavy)", "notes": "", "vocals": "Lennon", "year": "1969", "songwriters": "Lennon"},
"iwanttoholdyourhand": {"album": "UK: A Collection of Beatles Oldies US: Meet the Beatles!", "title": "I Want to Hold Your Hand", "notes": "", "vocals": "Lennon, McCartney", "year": "1963", "songwriters": "Lennon\nMcCartney"},
"iwanttotellyou": {"album": "Revolver", "title": "I Want to Tell You", "notes": "", "vocals": "Harrison", "year": "1966", "songwriters": "Harrison"},
"iwill": {"album": "The Beatles", "title": "I Will", "notes": "", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney"},
"illbeback": {"album": "UK: A Hard Day's Night US: Beatles '65", "title": "I'll Be Back", "notes": "", "vocals": "Lennon and McCartney)", "year": "1964", "songwriters": "Lennon"},
"illbeonmyway": {"album": "Live at the BBC", "title": "I'll Be on My Way", "notes": "Single by Billy J Kramer with the Dakotas\n(April 1963)", "vocals": "Lennon", "year": "1963", "songwriters": "McCartney"},
"illcryinstead": {"album": "UK: A Hard Day's Night US: Something New", "title": "I'll Cry Instead", "notes": "", "vocals": "Lennon", "year": "1964", "songwriters": "Lennon"},
"illfollowthesun": {"album": "UK: Beatles for Sale US: Beatles '65", "title": "I'll Follow the Sun", "notes": "", "vocals": "McCartney, with Lennon", "year": "1964", "songwriters": "McCartney"},
"illgetyou": {"album": "UK: Past Masters Volume 1 US: The Beatles' Second Album", "title": "I'll Get You", "notes": "Non-album single\nB-side of \"She Loves You\"", "vocals": "Lennon, with McCartney", "year": "1963", "songwriters": "Lennon\nMcCartney"},
"imdown": {"album": "Rock 'n' Roll Music", "title": "I'm Down", "notes": "Non-album single\nB-side of \"Help!\"", "vocals": "McCartney", "year": "1965", "songwriters": "McCartney"},
"imgonnasitrightdownandcryoveryou": {"album": "Live at the BBC", "title": "I'm Gonna Sit Right Down and Cry (Over You)", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Joe Thomas\nHoward Biggs"},
"imhappyjusttodancewithyou": {"album": "UK: A Hard Day's Night US: Something New", "title": "I'm Happy Just to Dance with You", "notes": "", "vocals": "Harrison", "year": "1964", "songwriters": "Lennon\nMcCartney"},
"iminlove": {"album": "The Beatles Bootleg Recordings 1963", "title": "I'm In Love", "notes": "Written for The Fourmost\n(single released November 1963)", "vocals": "Lennon", "year": "1963", "songwriters": "Lennon"},
"imlookingthroughyou": {"album": "Rubber Soul", "title": "I'm Looking Through You", "notes": "", "vocals": "McCartney, with Lennon", "year": "1965", "songwriters": "McCartney"},
"imonlysleeping": {"album": "UK: Revolver US: Yesterday and Today", "title": "I'm Only Sleeping", "notes": "", "vocals": "Lennon", "year": "1966", "songwriters": "Lennon"},
"imsotired": {"album": "The Beatles", "title": "I'm So Tired", "notes": "", "vocals": "Lennon", "year": "1968", "songwriters": "Lennon"},
"imtalkingaboutyou": {"album": "Live! at the Star-Club in Hamburg, Germany; 1962", "title": "I'm Talking About You", "notes": "Cover", "vocals": "Lennon", "year": "1962", "songwriters": "Chuck Berry"},
"imaloser": {"album": "UK: Beatles for Sale US: Beatles '65", "title": "I'm a Loser", "notes": "", "vocals": "Lennon", "year": "1964", "songwriters": "Lennon"},
"ivegotafeeling": {"album": "Let It Be", "title": "I've Got a Feeling", "notes": "", "vocals": "McCartney, with Lennon", "year": "1969", "songwriters": "McCartney\n(with Lennon)"},
"ivejustseenaface": {"album": "UK: Help! US: Rubber Soul", "title": "I've Just Seen a Face", "notes": "", "vocals": "McCartney", "year": "1965", "songwriters": "McCartney"},
"ififell": {"album": "UK: A Hard Day's Night US: Something New", "title": "If I Fell", "notes": "", "vocals": "Lennon, with McCartney", "year": "1964", "songwriters": "Lennon"},
"ifineededsomeone": {"album": "UK: Rubber Soul US: Yesterday and Today", "title": "If I Needed Someone", "notes": "", "vocals": "Harrison", "year": "1965", "songwriters": "Harrison"},
"ifyouvegottrouble": {"album": "Anthology 2", "title": "If You've Got Trouble", "notes": "", "vocals": "Starr", "year": "1965", "songwriters": "Lennon\nMcCartney"},
"inmylife": {"album": "Rubber Soul", "title": "In My Life", "notes": "", "vocals": "Lennon", "year": "1965", "songwriters": "Lennon\nMcCartney"},
"inspiteofallthedanger": {"album": "Anthology 1", "title": "In Spite of All the Danger", "notes": "", "vocals": "Lennon", "year": "1958", "songwriters": "McCartney and Harrison"},
"itwontbelong": {"album": "UK: With the Beatles US: Meet the Beatles!", "title": "It Won't Be Long", "notes": "", "vocals": "Lennon", "year": "1963", "songwriters": "Lennon\n(with McCartney)"},
"itsalltoomuch": {"album": "Yellow Submarine", "title": "It's All Too Much", "notes": "", "vocals": "Harrison", "year": "1967", "songwriters": "Harrison"},
"itsonlylove": {"album": "UK: Help! US: Rubber Soul", "title": "It's Only Love", "notes": "", "vocals": "Lennon", "year": "1965", "songwriters": "Lennon"},
"jazzpianosong": {"album": "Let it Be film", "title": "Jazz Piano Song", "notes": "", "vocals": "McCartney", "year": "1969", "songwriters": "McCartney\nStarr"},
"jessiesdream": {"album": "Magical Mystery Tour", "title": "Jessie's Dream", "notes": "", "vocals": "Instrumental", "year": "1967", "songwriters": "Lennon, McCartney, Harrison, Starr"},
"johnnybgoode": {"album": "Live at the BBC", "title": "Johnny B. Goode", "notes": "Cover", "vocals": "Lennon", "year": "1964", "songwriters": "Chuck Berry"},
"julia": {"album": "The Beatles", "title": "Julia", "notes": "", "vocals": "Lennon", "year": "1968", "songwriters": "Lennon"},
"junk": {"album": "Anthology 3", "title": "Junk", "notes": "", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney"},
"kansascityheyheyheyhey": {"album": "UK: Beatles for Sale US: Beatles VI", "title": "Kansas City/Hey-Hey-Hey-Hey!", "notes": "Cover", "vocals": "McCartney", "year": "1964", "songwriters": "Jerry Leiber and Mike Stoller/Little Richard"},
"keepyourhandsoffmybaby": {"album": "Live at the BBC", "title": "Keep Your Hands Off My Baby", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Gerry Goffin\nCarole King"},
"kommgibmirdeinehand": {"album": "UK: Rarities US: Something New", "title": "Komm, gib mir deine Hand", "notes": "Non-album single\nGerman version of \"I Want to Hold Your Hand\"", "vocals": "Lennon, McCartney", "year": "1964", "songwriters": "Lennon\nMcCartney\nJean Nicolas\nHeinz Hellmer"},
"ladymadonna": {"album": "UK: 1967-1970 US: Hey Jude", "title": "Lady Madonna", "notes": "Non-album single", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney\n(with Lennon)"},
"leavemykittenalone": {"album": "Anthology 1", "title": "Leave My Kitten Alone", "notes": "Cover", "vocals": "Lennon", "year": "1964", "songwriters": "Little Willie John\nTitus Turner\nJames McDougall"},
"lendmeyourcomb": {"album": "Anthology 1", "title": "Lend Me Your Comb", "notes": "Cover", "vocals": "Lennon, McCartney", "year": "1963", "songwriters": "Kay Twomey\nFred Wise\nBen Weisman"},
"letitbe": {"album": "Let It Be", "title": "Let It Be", "notes": "", "vocals": "McCartney", "year": "1969", "songwriters": "McCartney"},
"likedreamersdo": {"album": "Anthology 1", "title": "Like Dreamers Do", "notes": "Recorded by The Applejacks", "vocals": "McCartney", "year": "1962", "songwriters": "McCartney"},
"littlechild": {"album": "UK: With the Beatles US: Meet the Beatles!", "title": "Little Child", "notes": "", "vocals": "Lennon, McCartney", "year": "1963", "songwriters": "Lennon\nMcCartney"},
"lonesometearsinmyeyes": {"album": "Live at the BBC", "title": "Lonesome Tears in My Eyes", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Johnny Burnette\nDorsey Burnette\nPaul Burlison\nAl Mortimer"},
"longtallsally": {"album": "UK: Long Tall Sally EP US: The Beatles' Second Album", "title": "Long Tall Sally", "notes": "Non-album single\nCover", "vocals": "McCartney", "year": "1964", "songwriters": "Robert \"Bumps\" Blackwell\nEnotris Johnson\nLittle Richard"},
"longlonglong": {"album": "The Beatles", "title": "Long, Long, Long", "notes": "", "vocals": "Harrison", "year": "1968", "songwriters": "Harrison"},
"lookingglass": {"album": "", "title": "Looking Glass", "notes": "", "vocals": "McCartney", "year": "1962", "songwriters": "McCartney"},
"lovemedo": {"album": "UK: Please Please Me US: The Early Beatles", "title": "Love Me Do", "notes": "featuring Andy White on drums", "vocals": "McCartney, with Lennon", "year": "1962", "songwriters": "McCartney\n(with Lennon)"},
"loveyouto": {"album": "Revolver", "title": "Love You To", "notes": "", "vocals": "Harrison", "year": "1966", "songwriters": "Harrison"},
"loveoftheloved": {"album": "", "title": "Love of the Loved", "notes": "Single by Cilla Black\n(September 1963)", "vocals": "McCartney", "year": "1962", "songwriters": "McCartney\n(with Lennon)"},
"lovelyrita": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "title": "Lovely Rita", "notes": "", "vocals": "McCartney", "year": "1967", "songwriters": "McCartney"},
"lucille": {"album": "Live at the BBC", "title": "Lucille", "notes": "Cover", "vocals": "McCartney", "year": "1963", "songwriters": "Little Richard\nAlbert Collins"},
"lucyintheskywithdiamonds": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "title": "Lucy in the Sky with Diamonds", "notes": "", "vocals": "Lennon", "year": "1967", "songwriters": "Lennon"},
"madman": {"album": "N/A", "title": "Madman", "notes": "From Get Back/Let It Be sessions", "vocals": "Lennon", "year": "1969", "songwriters": "Lennon"},
"maggiemae": {"album": "Let It Be", "title": "Maggie Mae", "notes": "Cover", "vocals": "Lennon, with McCartney", "year": "1969", "songwriters": "Traditional, arr. Lennon, McCartney\nHarrison, Starr"},
"magicalmysterytour": {"album": "Magical Mystery Tour", "title": "Magical Mystery Tour", "notes": "", "vocals": "McCartney, with Lennon", "year": "1967", "songwriters": "McCartney\n(with Lennon)"},
"mailmanbringmenomoreblues": {"album": "Anthology 3", "title": "Mailman, Bring Me No More Blues", "notes": "Cover", "vocals": "Lennon", "year": "1969", "songwriters": "Ruth Roberts\nBill Katz\nStanley Clayton"},
"marthamydear": {"album": "The Beatles", "title": "Martha My Dear", "notes": "", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney"},
"matchbox": {"album": "UK: \"Long Tall Sally\" EP US: Something New", "title": "Matchbox", "notes": "Cover", "vocals": "Starr", "year": "1964", "songwriters": "Carl Perkins\nBlind Lemon Jefferson"},
"maxwellssilverhammer": {"album": "Abbey Road", "title": "Maxwell's Silver Hammer", "notes": "", "vocals": "McCartney", "year": "1969", "songwriters": "McCartney[56]"},
"meanmrmustard": {"album": "Abbey Road", "title": "Mean Mr. Mustard", "notes": "", "vocals": "Lennon, with McCartney", "year": "1969", "songwriters": "Lennon[58]"},
"memphistennessee": {"album": "Live at the BBC", "title": "Memphis, Tennessee", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Chuck Berry"},
"michelle": {"album": "Rubber Soul", "title": "Michelle", "notes": "", "vocals": "McCartney", "year": "1965", "songwriters": "McCartney\n(with Lennon)"},
"misery": {"album": "UK: Please Please Me US: Introducing… The Beatles", "title": "Misery", "notes": "", "vocals": "Lennon and McCartney", "year": "1963", "songwriters": "Lennon\n(with McCartney)"},
"moneythatswhatiwant": {"album": "UK: With the Beatles US: The Beatles Second Album", "title": "Money (That's What I Want)", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Berry Gordy\nJanie Bradford"},
"moonlightbay": {"album": "Anthology 1", "title": "Moonlight Bay", "notes": "Performed on the Morecambe and Wise Show in 2/12/63", "vocals": "Lennon, McCartney, Harrison, Eric Morecambe, Ernie Wise", "year": "1963", "songwriters": "Percy Wenrich\nEdward Madden"},
"mothernaturesson": {"album": "The Beatles", "title": "Mother Nature's Son", "notes": "", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney"},
"mrmoonlight": {"album": "UK: Beatles for Sale US: Beatles '65", "title": "Mr. Moonlight", "notes": "Cover", "vocals": "Lennon", "year": "1964", "songwriters": "Roy Lee Johnson"},
"noreply": {"album": "UK: Beatles for Sale US: Beatles '65", "title": "No Reply", "notes": "", "vocals": "Lennon, with McCartney", "year": "1964", "songwriters": "Lennon\n(with McCartney)"},
"norwegianwoodthisbirdhasflown": {"album": "Rubber Soul", "title": "Norwegian Wood (This Bird Has Flown)", "notes": "", "vocals": "Lennon", "year": "1965", "songwriters": "Lennon\n(with McCartney)"},
"notguilty": {"album": "Anthology 3", "title": "Not Guilty", "notes": "", "vocals": "Harrison", "year": "1968", "songwriters": "Harrison"},
"notasecondtime": {"album": "UK: With the Beatles US: Meet the Beatles!", "title": "Not a Second Time", "notes": "", "vocals": "Lennon", "year": "1963", "songwriters": "Lennon"},
"nothinshakinbuttheleavesonthetrees": {"album": "Live at the BBC", "title": "Nothin' Shakin' (But the Leaves on the Trees)", "notes": "Cover", "vocals": "Harrison", "year": "1963", "songwriters": "Eddie Fontaine"},
"nowhereman": {"album": "UK: Rubber Soul US: Yesterday and Today", "title": "Nowhere Man", "notes": "", "vocals": "Lennon, with McCartney and Harrison", "year": "1965", "songwriters": "Lennon\n(with McCartney)"},
"obladioblada": {"album": "The Beatles", "title": "Ob-La-Di, Ob-La-Da", "notes": "", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney"},
"octopussgarden": {"album": "Abbey Road", "title": "Octopus's Garden", "notes": "", "vocals": "Starr", "year": "1969", "songwriters": "Starkey[c]"},
"ohdarling": {"album": "Abbey Road", "title": "Oh! Darling", "notes": "", "vocals": "McCartney", "year": "1969", "songwriters": "McCartney[32]"},
"oldbrownshoe": {"album": "UK: 1967–1970 US: Hey Jude", "title": "Old Brown Shoe", "notes": "Non-album single\nB-side of \"The Ballad of John and Yoko\"", "vocals": "Harrison", "year": "1969", "songwriters": "Harrison"},
"oneafter": {"album": "Let It Be", "title": "One After 909", "notes": "", "vocals": "Lennon, with McCartney", "year": "1969", "songwriters": "Lennon"},
"oneandoneistwo": {"album": "", "title": "One and One Is Two", "notes": "Single by The Strangers with Mike Shannon\n(May 1964)", "vocals": "McCartney", "year": "1964", "songwriters": "McCartney"},
"onlyanorthernsong": {"album": "Yellow Submarine", "title": "Only a Northern Song", "notes": "", "vocals": "Harrison", "year": "1967", "songwriters": "Harrison"},
"oohmysoul": {"album": "Live at the BBC", "title": "Ooh! My Soul", "notes": "Cover", "vocals": "McCartney", "year": "1963", "songwriters": "Little Richard"},
"psiloveyou": {"album": "UK: Please Please Me US: The Early Beatles", "title": "P.S. I Love You", "notes": "", "vocals": "McCartney", "year": "1962", "songwriters": "McCartney\n(with Lennon)"},
"paperbackwriter": {"album": "UK: A Collection of Beatles Oldies US: Hey Jude", "title": "Paperback Writer", "notes": "Non-album single", "vocals": "McCartney", "year": "1966", "songwriters": "McCartney"},
"pennylane": {"album": "Magical Mystery Tour", "title": "Penny Lane", "notes": "Double A-side single\nwith \"Strawberry Fields Forever\"", "vocals": "McCartney", "year": "1966", "songwriters": "McCartney"},
"piggies": {"album": "The Beatles", "title": "Piggies", "notes": "", "vocals": "Harrison", "year": "1968", "songwriters": "Harrison"},
"pleasemrpostman": {"album": "UK: With the Beatles US: The Beatles' Second Album", "title": "Please Mr. Postman", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Georgia Dobbins\nWilliam Garrett\nBrian Holland\nRobert Bateman\nFreddie Gorman"},
"pleasepleaseme": {"album": "UK: Please Please Me US: The Early Beatles", "title": "Please Please Me", "notes": "Single", "vocals": "Lennon and McCartney", "year": "1962", "songwriters": "Lennon"},
"polythenepam": {"album": "Abbey Road", "title": "Polythene Pam", "notes": "", "vocals": "Lennon", "year": "1969", "songwriters": "Lennon"},
"rain": {"album": "UK: Rarities US: Hey Jude", "title": "Rain", "notes": "Non-album single\nB-side to \"Paperback Writer\"", "vocals": "Lennon", "year": "1966", "songwriters": "Lennon"},
"reallove": {"album": "Anthology 2", "title": "Real Love", "notes": "", "vocals": "Lennon", "year": "1980", "songwriters": "Lennon"},
"revolution": {"album": "UK: 1967-1970 US: Hey Jude", "title": "Revolution", "notes": "Non-album single\nB-side to \"Hey Jude\"", "vocals": "Lennon", "year": "1968", "songwriters": "Lennon"},
"revolution": {"album": "The Beatles", "title": "Revolution 1", "notes": "", "vocals": "Lennon", "year": "1968", "songwriters": "Lennon"},
"revolution": {"album": "The Beatles", "title": "Revolution 9", "notes": "", "vocals": "Sound Collage", "year": "1968", "songwriters": "Lennon\n(with Ono and Harrison)"},
"ripitupshakerattleandrollbluesuedeshoes": {"album": "Anthology 3", "title": "Rip It Up / Shake, Rattle, and Roll / Blue Suede Shoes", "notes": "Cover", "vocals": "Lennon, McCartney", "year": "1969", "songwriters": "Robert Blackwell, John Marascalco (\"Rip It Up\")\nCharles Calhoun(\"Shake, Rattle, and Roll\")\nCarl Perkins (\"Blue Suede Shoes\")"},
"rockandrollmusic": {"album": "UK: Beatles for Sale US: Beatles '65", "title": "Rock and Roll Music", "notes": "Cover", "vocals": "Lennon", "year": "1964", "songwriters": "Chuck Berry"},
"rockyraccoon": {"album": "The Beatles", "title": "Rocky Raccoon", "notes": "", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney\n(with Lennon)"},
"rolloverbeethoven": {"album": "UK: With the Beatles US: The Beatles' Second Album", "title": "Roll Over Beethoven", "notes": "Cover", "vocals": "Harrison", "year": "1963", "songwriters": "Chuck Berry"},
"runforyourlife": {"album": "Rubber Soul", "title": "Run for Your Life", "notes": "", "vocals": "Lennon", "year": "1965", "songwriters": "Lennon\n(with McCartney)"},
"savoytruffle": {"album": "The Beatles", "title": "Savoy Truffle", "notes": "", "vocals": "Harrison", "year": "1968", "songwriters": "Harrison"},
"searchin": {"album": "Anthology 1", "title": "Searchin'", "notes": "Cover", "vocals": "McCartney", "year": "1962", "songwriters": "Jerry Leiber and Mike Stoller"},
"septemberintherain": {"album": "", "title": "September in the Rain", "notes": "Cover", "vocals": "McCartney", "year": "1962", "songwriters": "Al Dubin\nHarry Warren"},
"sexysadie": {"album": "The Beatles", "title": "Sexy Sadie", "notes": "", "vocals": "Lennon", "year": "1968", "songwriters": "Lennon"},
"sgtpepperslonelyheartsclubband": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "title": "Sgt. Pepper's Lonely Hearts Club Band", "notes": "", "vocals": "McCartney, with Lennon, Harrison and Starr", "year": "1967", "songwriters": "McCartney"},
"sgtpepperslonelyheartsclubbandreprise": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "title": "Sgt. Pepper's Lonely Hearts Club Band (Reprise)", "notes": "", "vocals": "McCartney, Lennon, Harrison, Starr", "year": "1967", "songwriters": "McCartney"},
"shakininthesixties": {"album": "Unreleased", "title": "Shakin' in the Sixties", "notes": "", "vocals": "Lennon", "year": "1969", "songwriters": "Lennon"},
"shecameinthroughthebathroomwindow": {"album": "Abbey Road", "title": "She Came in Through the Bathroom Window", "notes": "", "vocals": "McCartney", "year": "1969", "songwriters": "McCartney"},
"shelovesyou": {"album": "UK: A Collection of Beatles Oldies US: The Beatles Second Album", "title": "She Loves You", "notes": "Non-album single", "vocals": "Lennon, McCartney", "year": "1963", "songwriters": "Lennon\nMcCartney"},
"shesaidshesaid": {"album": "Revolver", "title": "She Said She Said", "notes": "", "vocals": "Lennon", "year": "1966", "songwriters": "Lennon"},
"shesleavinghome": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "title": "She's Leaving Home", "notes": "", "vocals": "McCartney, with Lennon", "year": "1967", "songwriters": "McCartney\n(with Lennon)"},
"shesawoman": {"album": "UK: Rarities US: Beatles '65", "title": "She's a Woman", "notes": "Non-album single\nB-side to \"I Feel Fine\"", "vocals": "McCartney", "year": "1964", "songwriters": "McCartney\n(with Lennon)"},
"shout": {"album": "Anthology 1", "title": "Shout", "notes": "Cover", "vocals": "Lennon, McCartney, Harrison, Starr", "year": "1964", "songwriters": "Rudolph Isley\nRonald Isley\nO'Kelly Isley Jr."},
"sieliebtdich": {"album": "UK: Rarities US: Rarities", "title": "Sie liebt dich", "notes": "Non-album single\nGerman version of \"She Loves You\"", "vocals": "Lennon, McCartney", "year": "1964", "songwriters": "Lennon\nMcCartney\nJean Nicolas\nLee Montogue"},
"slowdown": {"album": "UK: \"Long Tall Sally\" EP US: Something New", "title": "Slow Down", "notes": "Non-album single\nB-side of \"Matchbox\"\nCover", "vocals": "Lennon", "year": "1964", "songwriters": "Larry Williams"},
"sohowcomenoonelovesme": {"album": "Live at the BBC", "title": "So How Come (No One Loves Me)", "notes": "Cover", "vocals": "Harrison", "year": "1963", "songwriters": "Felice and Boudleaux Bryant"},
"soldieroflovelaydownyourarms": {"album": "Live at the BBC", "title": "Soldier of Love (Lay Down Your Arms)", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Buzz Cason\nTony Moon"},
"someotherguy": {"album": "Live at the BBC", "title": "Some Other Guy", "notes": "Cover", "vocals": "Lennon, McCartney", "year": "1963", "songwriters": "Jerry Leiber and Mike Stoller\nRichie Barrett"},
"something": {"album": "Abbey Road", "title": "Something", "notes": "Double A-side single\nwith \"Come Together\"", "vocals": "Harrison", "year": "1969", "songwriters": "Harrison"},
"sourmilksea": {"album": "Unreleased", "title": "Sour Milk Sea", "notes": "White Album\"\" outtake", "vocals": "Harrison", "year": "1968", "songwriters": "Harrison"},
"stepinsidelovelosparanoias": {"album": "Anthology 3", "title": "Step Inside Love/Los Paranoias", "notes": "\"Step Inside Love\" was recorded by Cilla Black\n(1968)", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney (\"Step Inside Love\")\nLennon–McCartney\nHarrison–Starr (\"Los Paranoias\")"},
"strawberryfieldsforever": {"album": "Magical Mystery Tour", "title": "Strawberry Fields Forever", "notes": "Double A-side single\n(with \"Penny Lane\")", "vocals": "Lennon", "year": "1966", "songwriters": "Lennon"},
"sunking": {"album": "Abbey Road", "title": "Sun King", "notes": "", "vocals": "Lennon, with McCartney and Harrison", "year": "1969", "songwriters": "Lennon"},
"suretofallinlovewithyou": {"album": "Live at the BBC", "title": "Sure to Fall (in Love with You)", "notes": "Cover", "vocals": "McCartney", "year": "1963", "songwriters": "Carl Perkins\nQuinton Claunch\nBill Cantrell"},
"sweetlittlesixteen": {"album": "Live at the BBC", "title": "Sweet Little Sixteen", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Chuck Berry"},
"takegoodcareofmybaby": {"album": "", "title": "Take Good Care of My Baby", "notes": "Cover", "vocals": "Harrison", "year": "1962", "songwriters": "Gerry Goffin\nCarole King"},
"takingatriptocarolina": {"album": "Let It Be... Naked - Fly on the Wall bonus disc", "title": "Taking a Trip to Carolina", "notes": "", "vocals": "Starr", "year": "1969", "songwriters": "Starr"},
"taxman": {"album": "Revolver", "title": "Taxman", "notes": "McCartney plays guitar solo", "vocals": "Harrison, with Lennon and McCartney", "year": "1966", "songwriters": "Harrison"},
"teddyboy": {"album": "Anthology 3", "title": "Teddy Boy", "notes": "\"Let It Be\" outtake", "vocals": "McCartney", "year": "1969", "songwriters": "McCartney"},
"tellmewhatyousee": {"album": "UK: Help! US: Beatles VI", "title": "Tell Me What You See", "notes": "", "vocals": "McCartney, with Lennon", "year": "1965", "songwriters": "McCartney\n(with Lennon)"},
"tellmewhy": {"album": "UK: A Hard Day's Night US: Something New", "title": "Tell Me Why", "notes": "", "vocals": "Lennon", "year": "1964", "songwriters": "Lennon"},
"thankyougirl": {"album": "UK: Rarities US: The Beatles Second Album", "title": "Thank You Girl", "notes": "Non-album single\nB-side of \"From Me To You\"", "vocals": "Lennon, McCartney", "year": "1963", "songwriters": "Lennon\nMcCartney"},
"thatmeansalot": {"album": "Anthology 2", "title": "That Means a Lot", "notes": "Recorded by P.J. Proby\n(1965)", "vocals": "McCartney", "year": "1965", "songwriters": "McCartney"},
"thatllbetheday": {"album": "Anthology 1", "title": "That'll Be the Day", "notes": "Cover", "vocals": "Lennon", "year": "1958", "songwriters": "Jerry Allison\nBuddy Holly\nNorman Petty"},
"thatsallrightmama": {"album": "Live at the BBC", "title": "That’s All Right (Mama)", "notes": "Cover", "vocals": "McCartney", "year": "1963", "songwriters": "Arthur Crudup"},
"theballadofjohnandyoko": {"album": "UK: 1967–1970 US: Hey Jude", "title": "The Ballad of John and Yoko", "notes": "", "vocals": "Lennon, with McCartney", "year": "1969", "songwriters": "Lennon"},
"thecontinuingstoryofbungalowbill": {"album": "The Beatles", "title": "The Continuing Story of Bungalow Bill", "notes": "", "vocals": "Lennon", "year": "1968", "songwriters": "Lennon"},
"theend": {"album": "Abbey Road", "title": "The End", "notes": "", "vocals": "McCartney", "year": "1969", "songwriters": "McCartney"},
"thefoolonthehill": {"album": "Magical Mystery Tour", "title": "The Fool on the Hill", "notes": "", "vocals": "McCartney", "year": "1967", "songwriters": "McCartney"},
"thehoneymoonsong": {"album": "Live at the BBC", "title": "The Honeymoon Song", "notes": "Cover", "vocals": "McCartney", "year": "1963", "songwriters": "Mikis Theodorakis\nSansom"},
"theinnerlight": {"album": "UK: Rarities US: Rarities", "title": "The Inner Light", "notes": "Non-album single\nB-side of \"Lady Madonna\"", "vocals": "Harrison", "year": "1968", "songwriters": "Harrison"},
"thelongandwindingroad": {"album": "Let It Be", "title": "The Long and Winding Road", "notes": "", "vocals": "McCartney", "year": "1969", "songwriters": "McCartney"},
"thenightbefore": {"album": "Help!", "title": "The Night Before", "notes": "", "vocals": "McCartney", "year": "1965", "songwriters": "McCartney"},
"thesheikofaraby": {"album": "Anthology 1", "title": "The Sheik of Araby", "notes": "Cover", "vocals": "Harrison", "year": "1962", "songwriters": "Harry B. Smith\nFrancis Wheeler\nTed Snyder"},
"theword": {"album": "Rubber Soul", "title": "The Word", "notes": "", "vocals": "Lennon, with McCartney and Harrison", "year": "1965", "songwriters": "Lennon\nMcCartney"},
"theresaplace": {"album": "UK: Please Please Me US: Rarities", "title": "There's a Place", "notes": "", "vocals": "Lennon, McCartney", "year": "1963", "songwriters": "Lennon\nMcCartney"},
"thingswesaidtoday": {"album": "UK: A Hard Day's Night US: Something New", "title": "Things We Said Today", "notes": "", "vocals": "McCartney", "year": "1964", "songwriters": "McCartney"},
"thinkforyourself": {"album": "Rubber Soul", "title": "Think for Yourself", "notes": "", "vocals": "Harrison", "year": "1965", "songwriters": "Harrison"},
"thisboy": {"album": "UK: Rarities US: Meet the Beatles!", "title": "This Boy", "notes": "Non-album single\nB-side of \"I Want To Hold Your Hand\"", "vocals": "Lennon, with McCartney and Harrison", "year": "1963", "songwriters": "Lennon"},
"threecoolcats": {"album": "Anthology 1", "title": "Three Cool Cats", "notes": "Cover", "vocals": "Harrison", "year": "1962", "songwriters": "Jerry Leiber and Mike Stoller"},
"tickettoride": {"album": "Help!", "title": "Ticket to Ride", "notes": "", "vocals": "Lennon, with McCartney", "year": "1965", "songwriters": "Lennon"},
"tilltherewasyou": {"album": "UK: With the Beatles US: Meet the Beatles!", "title": "Till There Was You", "notes": "Cover", "vocals": "McCartney", "year": "1963", "songwriters": "Meredith Willson"},
"tipofmytongue": {"album": "Unreleased", "title": "Tip of My Tongue", "notes": "Recorded by Tommy Quickly\n(Released in 1963)", "vocals": "Lennon, McCartney", "year": "", "songwriters": "Lennon\nMcCartney"},
"toknowheristoloveher": {"album": "Live at the BBC", "title": "To Know Her is to Love Her", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Phil Spector"},
"tomorrowneverknows": {"album": "Revolver", "title": "Tomorrow Never Knows", "notes": "", "vocals": "Lennon", "year": "1966", "songwriters": "Lennon"},
"toomuchmonkeybusiness": {"album": "Live at the BBC", "title": "Too Much Monkey Business", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Chuck Berry"},
"twistandshout": {"album": "UK: Please Please Me US: The Early Beatles", "title": "Twist and Shout", "notes": "Cover", "vocals": "Lennon", "year": "1963", "songwriters": "Phil Medley\nBert Berns"},
"twoofus": {"album": "Let It Be", "title": "Two of Us", "notes": "", "vocals": "McCartney, with Lennon", "year": "1969", "songwriters": "McCartney"},
"wait": {"album": "Rubber Soul", "title": "Wait", "notes": "", "vocals": "McCartney and Lennon", "year": "1965", "songwriters": "McCartney\n(with Lennon)"},
"watchingrainbows": {"album": "", "title": "Watching Rainbows", "notes": "", "vocals": "Lennon", "year": "1969", "songwriters": "Lennon\nand McCartney"},
"wecanworkitout": {"album": "UK: A Collection of Beatles Oldies US: Yesterday and Today", "title": "We Can Work It Out", "notes": "Non-album single\nDouble A-side with \"Day Tripper\"", "vocals": "McCartney, with Lennon", "year": "1965", "songwriters": "McCartney\n(with Lennon)"},
"whatgoeson": {"album": "UK: Rubber Soul US: Yesterday and Today", "title": "What Goes On", "notes": "", "vocals": "Starr", "year": "1965", "songwriters": "Lennon\nMcCartney\nStarkey[d]"},
"whatyouredoing": {"album": "UK: Beatles for Sale US: Beatles VI", "title": "What You're Doing", "notes": "", "vocals": "McCartney", "year": "1964", "songwriters": "McCartney"},
"whatsthenewmaryjane": {"album": "Anthology 3", "title": "What's The New Mary Jane", "notes": "\"White Album\" outtake", "vocals": "Lennon", "year": "1968", "songwriters": "Lennon"},
"whenigethome": {"album": "UK: A Hard Day's Night US: Something New", "title": "When I Get Home", "notes": "", "vocals": "Lennon", "year": "1964", "songwriters": "Lennon"},
"whenimsixtyfour": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "title": "When I'm Sixty-Four", "notes": "", "vocals": "McCartney", "year": "1966", "songwriters": "McCartney"},
"whilemyguitargentlyweeps": {"album": "The Beatles", "title": "While My Guitar Gently Weeps", "notes": "Eric Clapton plays lead guitar\n(uncredited)", "vocals": "Harrison", "year": "1968", "songwriters": "Harrison"},
"whydontwedoitintheroad": {"album": "The Beatles", "title": "Why Don't We Do It in the Road?", "notes": "", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney"},
"wildhoneypie": {"album": "The Beatles", "title": "Wild Honey Pie", "notes": "", "vocals": "McCartney", "year": "1968", "songwriters": "McCartney"},
"withalittlehelpfrommyfriends": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "title": "With a Little Help from My Friends", "notes": "", "vocals": "Starr, with Lennon and McCartney", "year": "1967", "songwriters": "Lennon\nMcCartney"},
"withinyouwithoutyou": {"album": "Sgt. Pepper's Lonely Hearts Club Band", "title": "Within You Without You", "notes": "", "vocals": "Lennon", "year": "1967", "songwriters": "Lennon"},
"woman": {"album": "Let It Be film", "title": "Woman", "notes": "Single by Peter and Gordon\n(January 1966)", "vocals": "McCartney", "year": "1965", "songwriters": "McCartney (as Bernard Webb)"},
"wordsoflove": {"album": "UK: Beatles for Sale US: Beatles VI", "title": "Words of Love", "notes": "Cover", "vocals": "Lennon, McCartney", "year": "1964", "songwriters": "Buddy Holly"},
"yellowsubmarine": {"album": "Revolver", "title": "Yellow Submarine", "notes": "", "vocals": "Starr", "year": "1966", "songwriters": "McCartney\n(with Lennon)"},
"yerblues": {"album": "The Beatles", "title": "Yer Blues", "notes": "", "vocals": "Lennon", "year": "1968", "songwriters": "Lennon"},
"yesitis": {"album": "UK: Rarities US: Beatles VI", "title": "Yes It Is", "notes": "Non-album single\nB-side of \"Ticket to Ride\"", "vocals": "Lennon, McCartney and Harrison", "year": "1965", "songwriters": "Lennon"},
"yesterday": {"album": "UK: Help! US: Yesterday and Today", "title": "Yesterday", "notes": "", "vocals": "McCartney", "year": "1965", "songwriters": "McCartney"},
"youcantdothat": {"album": "UK: A Hard Day's Night US: The Beatles Second Album", "title": "You Can't Do That", "notes": "", "vocals": "Lennon", "year": "1964", "songwriters": "Lennon"},
"youknowmynamelookupthenumber": {"album": "UK: Rarities US: Rarities", "title": "You Know My Name (Look Up the Number)", "notes": "Non-album single\nB-side of \"Let It Be\"", "vocals": "Lennon, McCartney", "year": "1967", "songwriters": "Lennon\n(with McCartney)"},
"youknowwhattodo": {"album": "Anthology 1", "title": "You Know What to Do", "notes": "", "vocals": "Harrison", "year": "1964", "songwriters": "Harrison"},
"youlikemetoomuch": {"album": "UK: Help! US: Beatles VI", "title": "You Like Me Too Much", "notes": "", "vocals": "Harrison", "year": "1965", "songwriters": "Harrison"},
"younevergivemeyourmoney": {"album": "Abbey Road", "title": "You Never Give Me Your Money", "notes": "", "vocals": "McCartney", "year": "1969", "songwriters": "McCartney[61]"},
"youwontseeme": {"album": "Rubber Soul", "title": "You Won't See Me", "notes": "", "vocals": "McCartney", "year": "1965", "songwriters": "McCartney"},
"youllbemine": {"album": "Anthology 1", "title": "You'll Be Mine", "notes": "", "vocals": "McCartney", "year": "1960", "songwriters": "Lennon\nMcCartney"},
"youregoingtolosethatgirl": {"album": "Help!", "title": "You're Going to Lose That Girl", "notes": "", "vocals": "Lennon", "year": "1965", "songwriters": "Lennon"},
"youvegottohideyourloveaway": {"album": "Help!", "title": "You've Got to Hide Your Love Away", "notes": "", "vocals": "Lennon", "year": "1965", "songwriters": "Lennon"},
"youvereallygotaholdonme": {"album": "UK: With the Beatles US: The Beatles Second Album", "title": "You've Really Got a Hold on Me", "notes": "Cover", "vocals": "Lennon and Harrison", "year": "1963", "songwriters": "Smokey Robinson"},
"youngblood": {"album": "Live at the BBC", "title": "Young Blood", "notes": "Cover", "vocals": "Harrison", "year": "1963", "songwriters": "Jerry Leiber and Mike Stoller"},
"yourmothershouldknow": {"album": "Magical Mystery Tour", "title": "Your Mother Should Know", "notes": "", "vocals": "McCartney", "year": "1967", "songwriters": "McCartney"},
}

if __name__ == '__main__':
    main()
