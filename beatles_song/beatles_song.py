#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
from difflib import SequenceMatcher

__version__ = '0.1.0'

re_brackets = re.compile(r'\([^()]+\)')

DEBUG = False
MATCH_MODE = 'rank'
MATCH_LIMIT = 1
MATCH_RATIO = 0.75
FMT = '{title} - {vocals}, {year}'
LIST_ALL = False
SHOW_ENVS = False

global_keys = ['DEBUG', 'MATCH_MODE', 'MATCH_LIMIT', 'MATCH_RATIO', 'FMT', 'LIST_ALL', 'SHOW_ENVS']

def debugp(s):
    if DEBUG:
        print('DEBUG: ' + s)

def match_songs(query, mode):
    # remove `(xxx)`
    query = re_brackets.sub('', query)
    # keep only alpha
    sig = ''.join(i for i in query if i.isalpha()).lower()

    if mode == 'rank':
        return rank_match(sig, MATCH_RATIO, MATCH_LIMIT)
    if mode == 'fuzzy':
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

    debugp('global vars: MATCH_MODE={} MATCH_RATIO={} MATCH_LIMIT={} FMT={}'.format(
        MATCH_MODE, MATCH_RATIO, MATCH_LIMIT, FMT,
    ))
    # match songs
    try:
        matched = match_songs(query, MATCH_MODE)
    except ValueError as e:
        print(str(e))
        sys.exit(1)

    for s in matched:
        print(format_output_line(s))
    else:
        sys.exit(1)

songs = {
"baroriginal": {"title": "12-Bar Original", "album": "Anthology 2", "songwriters": "John Lennon\nPaul McCartney\nGeorge Harrison\nRingo Starr", "vocals": "Instrumental", "year": "1965", "notes": ""},
"adayinthelife": {"title": "A Day in the Life", "album": "Sgt. Pepper's Lonely Hearts Club Band", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon, McCartney", "year": "1967", "notes": ""},
"aharddaysnight": {"title": "A Hard Day's Night", "album": "UK: A Hard Day's Night US: 1962–1966", "songwriters": "Lennon\n(with McCartney)", "vocals": "Lennon, with McCartney", "year": "1964", "notes": ""},
"ashotofrhythmandblues": {"title": "A Shot of Rhythm and Blues", "album": "Live at the BBC", "songwriters": "Terry Thompson", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"atasteofhoney": {"title": "A Taste of Honey", "album": "UK: Please Please Me US: The Early Beatles", "songwriters": "Bobby Scott\nRic Marlow", "vocals": "McCartney", "year": "1963", "notes": "Cover"},
"acrosstheuniverse": {"title": "Across the Universe", "album": "Let It Be", "songwriters": "Lennon", "vocals": "Lennon", "year": "1968", "notes": ""},
"actnaturally": {"title": "Act Naturally", "album": "UK: Help! US: Yesterday and Today", "songwriters": "Johnny Russell\nVoni Morrison", "vocals": "Starr", "year": "1965", "notes": "Cover"},
"aintshesweet": {"title": "Ain't She Sweet", "album": "Anthology 1", "songwriters": "Jack Yellen\nMilton Ager", "vocals": "Lennon", "year": "1961", "notes": "Cover"},
"allivegottodo": {"title": "All I've Got to Do", "album": "UK: With the Beatles US: Meet the Beatles!", "songwriters": "Lennon", "vocals": "Lennon", "year": "1963", "notes": ""},
"allmyloving": {"title": "All My Loving", "album": "UK: With the Beatles US: Meet the Beatles!", "songwriters": "McCartney", "vocals": "McCartney", "year": "1963", "notes": ""},
"allthingsmustpass": {"title": "All Things Must Pass", "album": "Anthology 3", "songwriters": "Harrison", "vocals": "Harrison", "year": "1969", "notes": ""},
"alltogethernow": {"title": "All Together Now", "album": "Yellow Submarine", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney", "year": "1967", "notes": ""},
"allyouneedislove": {"title": "All You Need Is Love", "album": "Magical Mystery Tour", "songwriters": "Lennon", "vocals": "Lennon", "year": "1967", "notes": ""},
"andiloveher": {"title": "And I Love Her", "album": "UK: A Hard Day's Night US: Something New", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney", "year": "1964", "notes": ""},
"andyourbirdcansing": {"title": "And Your Bird Can Sing", "album": "UK: Revolver US: Yesterday and Today", "songwriters": "Lennon\n(with McCartney)", "vocals": "Lennon", "year": "1966", "notes": ""},
"annagotohim": {"title": "Anna (Go to Him)", "album": "UK: Please Please Me US: The Early Beatles", "songwriters": "Arthur Alexander", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"anothergirl": {"title": "Another Girl", "album": "Help!", "songwriters": "McCartney", "vocals": "McCartney", "year": "1965", "notes": ""},
"anytimeatall": {"title": "Any Time at All", "album": "UK: A Hard Day's Night US: Something New", "songwriters": "Lennon\n(with McCartney)", "vocals": "Lennon", "year": "1964", "notes": ""},
"askmewhy": {"title": "Ask Me Why", "album": "UK: Please Please Me US: The Early Beatles", "songwriters": "Lennon\n(with McCartney)", "vocals": "Lennon", "year": "1962", "notes": ""},
"babyitsyou": {"title": "Baby It's You", "album": "UK: Please Please Me US: The Early Beatles", "songwriters": "Burt Bacharach\nHal David\nLuther Dixon", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"babysinblack": {"title": "Baby's in Black", "album": "UK: Beatles for Sale US: Beatles '65", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon, McCartney", "year": "1964", "notes": ""},
"babyyourearichman": {"title": "Baby, You're a Rich Man", "album": "Magical Mystery Tour", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon", "year": "1967", "notes": "Non-album single\nB-side of \"All You Need is Love\""},
"backintheussr": {"title": "Back in the U.S.S.R.", "album": "The Beatles", "songwriters": "McCartney", "vocals": "McCartney", "year": "1968", "notes": ""},
"badboy": {"title": "Bad Boy", "album": "UK: A Collection of Beatles Oldies US: Beatles VI", "songwriters": "Larry Williams", "vocals": "Lennon", "year": "1965", "notes": "Cover"},
"badtome": {"title": "Bad to Me", "album": "The Beatles Bootleg Recordings 1963", "songwriters": "Lennon", "vocals": "Lennon", "year": "1963", "notes": "Written for Billy J. Kramer"},
"beautifuldreamer": {"title": "Beautiful Dreamer", "album": "On Air – Live at the BBC Volume 2", "songwriters": "Stephen Foster", "vocals": "McCartney", "year": "1963", "notes": "Cover"},
"because": {"title": "Because", "album": "Abbey Road", "songwriters": "Lennon[25]", "vocals": "Lennon, McCartney, Harrison", "year": "1969", "notes": ""},
"becauseiknowyoulovemeso": {"title": "Because I Know You Love Me So", "album": "Let It Be... Naked - Fly on the Wall bonus disc", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon, McCartney", "year": "1969", "notes": ""},
"beingforthebenefitofmrkite": {"title": "Being for the Benefit of Mr. Kite!", "album": "Sgt. Pepper's Lonely Hearts Club Band", "songwriters": "Lennon", "vocals": "Lennon", "year": "1967", "notes": ""},
"birthday": {"title": "Birthday", "album": "The Beatles", "songwriters": "Lennon\nMcCartney", "vocals": "McCartney, with Lennon", "year": "1968", "notes": ""},
"blackbird": {"title": "Blackbird", "album": "The Beatles", "songwriters": "McCartney", "vocals": "McCartney", "year": "1968", "notes": ""},
"bluejayway": {"title": "Blue Jay Way", "album": "Magical Mystery Tour", "songwriters": "Harrison", "vocals": "Harrison", "year": "1967", "notes": ""},
"boys": {"title": "Boys", "album": "UK: Please Please Me US: The Early Beatles", "songwriters": "Luther Dixon\nWes Farrell", "vocals": "Starr", "year": "1963", "notes": "Cover"},
"bésamemucho": {"title": "Bésame Mucho", "album": "Anthology 1", "songwriters": "Consuelo Velázquez\nSunny Skylar", "vocals": "McCartney", "year": "1962", "notes": "Cover"},
"cantbuymelove": {"title": "Can't Buy Me Love", "album": "UK: A Hard Day's Night US: Hey Jude", "songwriters": "McCartney", "vocals": "McCartney, with Lennon", "year": "1964", "notes": ""},
"carol": {"title": "Carol", "album": "Live at the BBC", "songwriters": "Chuck Berry", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"carrythatweight": {"title": "Carry That Weight", "album": "Abbey Road", "songwriters": "McCartney[32]", "vocals": "McCartney, with Lennon, Harrison, and Starr", "year": "1969", "notes": ""},
"catswalk": {"title": "Catswalk", "album": "N/A", "songwriters": "McCartney", "vocals": "N/A", "year": "1962", "notes": ""},
"cayenne": {"title": "Cayenne", "album": "Anthology 1", "songwriters": "McCartney", "vocals": "Instrumental", "year": "1960", "notes": ""},
"chains": {"title": "Chains", "album": "UK: Please Please Me US: The Early Beatles", "songwriters": "Gerry Goffin\nCarole King", "vocals": "Harrison, (with Lennon, McCartney)", "year": "1963", "notes": "Cover"},
"childofnature": {"title": "Child of Nature", "album": "Let It Be... Naked - Fly on the Wall bonus disc", "songwriters": "Lennon", "vocals": "Lennon", "year": "1968", "notes": "Turned into Lennon's \"Jealous Guy\""},
"christmastimeishereagain": {"title": "Christmas Time (Is Here Again)", "album": "The Beatles' Christmas Album", "songwriters": "Lennon\nMcCartney\nHarrison\nStarr", "vocals": "Lennon, McCartney, Harrison, Starr", "year": "1967", "notes": "Non-album single\nB-side of \"Free As A Bird\""},
"circles": {"title": "Circles", "album": "", "songwriters": "Harrison", "vocals": "Harrison", "year": "1968", "notes": "On Harrison's Gone Troppo"},
"clarabella": {"title": "Clarabella", "album": "Live at the BBC", "songwriters": "Mike Pingitore", "vocals": "McCartney", "year": "1963", "notes": "Cover"},
"cometogether": {"title": "Come Together", "album": "Abbey Road", "songwriters": "Lennon[33]", "vocals": "Lennon", "year": "1969", "notes": "Double A-side single with \"Something\""},
"comeandgetit": {"title": "Come and Get It", "album": "Anthology 3", "songwriters": "McCartney", "vocals": "McCartney", "year": "1969", "notes": "Recorded by Badfinger"},
"crybabycry": {"title": "Cry Baby Cry", "album": "The Beatles", "songwriters": "Lennon", "vocals": "Lennon, with McCartney", "year": "1968", "notes": ""},
"cryforashadow": {"title": "Cry for a Shadow", "album": "Anthology 1", "songwriters": "Lennon and Harrison", "vocals": "Instrumental", "year": "1961", "notes": ""},
"cryingwaitinghoping": {"title": "Crying, Waiting, Hoping", "album": "Live at the BBC", "songwriters": "Buddy Holly", "vocals": "Harrison", "year": "1963", "notes": "Cover"},
"daytripper": {"title": "Day Tripper", "album": "UK: A Collection of Beatles Oldies US: Yesterday and Today", "songwriters": "Lennon\n(with McCartney)", "vocals": "Lennon, McCartney", "year": "1965", "notes": "Double A-side with \"We Can Work It Out\""},
"dearprudence": {"title": "Dear Prudence", "album": "The Beatles", "songwriters": "Lennon", "vocals": "Lennon", "year": "1968", "notes": "McCartney on drums"},
"devilinherheart": {"title": "Devil in Her Heart", "album": "UK: With the Beatles US: The Beatles' Second Album", "songwriters": "Drapkin (a.k.a. Ricky Dee)", "vocals": "Harrison", "year": "1963", "notes": "Cover"},
"digit": {"title": "Dig It", "album": "Let It Be", "songwriters": "Lennon\nMcCartney\nHarrison\nStarr", "vocals": "Lennon", "year": "1969", "notes": ""},
"digapony": {"title": "Dig a Pony", "album": "Let It Be", "songwriters": "Lennon", "vocals": "Lennon", "year": "1969", "notes": ""},
"dizzymisslizzy": {"title": "Dizzy, Miss Lizzy", "album": "UK: Help! US: Beatles VI", "songwriters": "Larry Williams", "vocals": "Lennon", "year": "1965", "notes": "Cover"},
"doyouwanttoknowasecret": {"title": "Do You Want to Know a Secret?", "album": "UK: Please Please Me US: The Early Beatles", "songwriters": "Lennon", "vocals": "Harrison", "year": "1963", "notes": ""},
"doctorrobert": {"title": "Doctor Robert", "album": "UK: Revolver US: Yesterday and Today", "songwriters": "Lennon\n(with McCartney)", "vocals": "Lennon", "year": "1966", "notes": ""},
"dontbotherme": {"title": "Don't Bother Me", "album": "UK: With the Beatles US: Meet the Beatles!", "songwriters": "Harrison", "vocals": "Harrison", "year": "1963", "notes": ""},
"donteverchange": {"title": "Don't Ever Change", "album": "Live at the BBC", "songwriters": "Gerry Goffin\nCarole King", "vocals": "Harrison and McCartney", "year": "1963", "notes": "Cover"},
"dontletmedown": {"title": "Don't Let Me Down", "album": "UK: 1967–1970 US: Hey Jude", "songwriters": "Lennon", "vocals": "Lennon (with McCartney)", "year": "1969", "notes": "Non-album single\nB-side of \"Get Back\""},
"dontpassmeby": {"title": "Don't Pass Me By", "album": "The Beatles", "songwriters": "Starkey[b]", "vocals": "Starr", "year": "1968", "notes": ""},
"drivemycar": {"title": "Drive My Car", "album": "UK: Rubber Soul US: Yesterday and Today", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney, with Lennon", "year": "1965", "notes": ""},
"eightdaysaweek": {"title": "Eight Days a Week", "album": "UK: Beatles for Sale US: Beatles VI", "songwriters": "McCartney\n(with Lennon)", "vocals": "Lennon, with McCartney", "year": "1964", "notes": "US single only"},
"eleanorrigby": {"title": "Eleanor Rigby", "album": "Revolver", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney", "year": "1966", "notes": ""},
"etcetera": {"title": "Etcetera", "album": "Unreleased", "songwriters": "McCartney", "vocals": "McCartney", "year": "1968", "notes": ""},
"everylittlething": {"title": "Every Little Thing", "album": "UK: Beatles for Sale US: Beatles VI", "songwriters": "McCartney", "vocals": "Lennon, with McCartney", "year": "1964", "notes": ""},
"everybodysgotsomethingtohideexceptmeandmymonkey": {"title": "Everybody's Got Something to Hide Except Me and My Monkey", "album": "The Beatles", "songwriters": "Lennon", "vocals": "Lennon", "year": "1968", "notes": ""},
"everybodystryingtobemybaby": {"title": "Everybody's Trying to Be My Baby", "album": "UK: Beatles for Sale US: Beatles '65", "songwriters": "Carl Perkins", "vocals": "Harrison", "year": "1964", "notes": "Cover"},
"fancymychanceswithyou": {"title": "Fancy My Chances with You", "album": "Let It Be... Naked - Fly on the Wall bonus disc", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon, McCartney", "year": "1969", "notes": ""},
"fixingahole": {"title": "Fixing a Hole", "album": "Sgt. Pepper's Lonely Hearts Club Band", "songwriters": "McCartney", "vocals": "McCartney", "year": "1967", "notes": ""},
"flying": {"title": "Flying", "album": "Magical Mystery Tour", "songwriters": "Lennon\nMcCartney\nHarrison\nStarr", "vocals": "Instrumental", "year": "1967", "notes": ""},
"fornoone": {"title": "For No One", "album": "Revolver", "songwriters": "McCartney", "vocals": "McCartney", "year": "1966", "notes": "Featuring Alan Civil on French horn"},
"foryoublue": {"title": "For You Blue", "album": "Let It Be", "songwriters": "Harrison", "vocals": "Harrison", "year": "1969", "notes": ""},
"freeasabird": {"title": "Free as a Bird", "album": "Anthology 1", "songwriters": "Lennon\nMcCartney\nHarrison\nStarr", "vocals": "Lennon, McCartney and Harrison", "year": "1977", "notes": ""},
"frommetoyou": {"title": "From Me to You", "album": "UK: A Collection of Beatles Oldies US: 1962–1966", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon, McCartney", "year": "1963", "notes": "Non-album single"},
"fromustoyou": {"title": "From Us to You", "album": "Live at the BBC", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon, McCartney", "year": "1963", "notes": ""},
"getback": {"title": "Get Back", "album": "Let It Be", "songwriters": "McCartney", "vocals": "McCartney", "year": "1969", "notes": ""},
"gettingbetter": {"title": "Getting Better", "album": "Sgt. Pepper's Lonely Hearts Club Band", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney, with Lennon", "year": "1967", "notes": ""},
"girl": {"title": "Girl", "album": "Rubber Soul", "songwriters": "Lennon", "vocals": "Lennon", "year": "1965", "notes": ""},
"gladallover": {"title": "Glad All Over", "album": "Live at the BBC", "songwriters": "Roy C. Bennett\nSid Tepper\nAaron Schroeder", "vocals": "Harrison", "year": "1963", "notes": "Cover"},
"glassonion": {"title": "Glass Onion", "album": "The Beatles", "songwriters": "Lennon", "vocals": "Lennon", "year": "1968", "notes": ""},
"goldenslumbers": {"title": "Golden Slumbers", "album": "Abbey Road", "songwriters": "McCartney[32]", "vocals": "McCartney", "year": "1969", "notes": ""},
"gooddaysunshine": {"title": "Good Day Sunshine", "album": "Revolver", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney", "year": "1966", "notes": ""},
"goodmorninggoodmorning": {"title": "Good Morning Good Morning", "album": "Sgt. Pepper's Lonely Hearts Club Band", "songwriters": "Lennon", "vocals": "Lennon", "year": "1967", "notes": "McCartney plays guitar solo"},
"goodnight": {"title": "Good Night", "album": "The Beatles", "songwriters": "Lennon", "vocals": "Starr", "year": "1968", "notes": ""},
"goodbye": {"title": "Goodbye", "album": "", "songwriters": "McCartney", "vocals": "McCartney", "year": "1969", "notes": ""},
"gottogetyouintomylife": {"title": "Got to Get You into My Life", "album": "Revolver", "songwriters": "McCartney", "vocals": "McCartney", "year": "1966", "notes": ""},
"hallelujahiloveherso": {"title": "Hallelujah, I Love Her So", "album": "Anthology 1", "songwriters": "Ray Charles", "vocals": "McCartney", "year": "1960", "notes": "Cover"},
"happinessisawarmgun": {"title": "Happiness Is a Warm Gun", "album": "The Beatles", "songwriters": "Lennon", "vocals": "Lennon", "year": "1968", "notes": ""},
"heather": {"title": "Heather", "album": "", "songwriters": "McCartney", "vocals": "McCartney", "year": "1968", "notes": "Donovan plays on the demo"},
"hellolittlegirl": {"title": "Hello Little Girl", "album": "Anthology 1", "songwriters": "Lennon", "vocals": "Lennon", "year": "1962", "notes": "Recorded by The Fourmost\nreleased August 1963"},
"hellogoodbye": {"title": "Hello, Goodbye", "album": "Magical Mystery Tour", "songwriters": "McCartney", "vocals": "McCartney", "year": "1967", "notes": ""},
"help": {"title": "Help!", "album": "Help!", "songwriters": "Lennon\n(with McCartney)", "vocals": "Lennon", "year": "1965", "notes": ""},
"helterskelter": {"title": "Helter Skelter", "album": "The Beatles", "songwriters": "McCartney", "vocals": "McCartney", "year": "1968", "notes": "Featuring Starr with shouted words in stereo version"},
"hermajesty": {"title": "Her Majesty", "album": "Abbey Road", "songwriters": "McCartney", "vocals": "McCartney", "year": "1969", "notes": ""},
"herecomesthesun": {"title": "Here Comes the Sun", "album": "Abbey Road", "songwriters": "Harrison", "vocals": "Harrison", "year": "1969", "notes": ""},
"herethereandeverywhere": {"title": "Here, There and Everywhere", "album": "Revolver", "songwriters": "McCartney", "vocals": "McCartney", "year": "1966", "notes": ""},
"heybulldog": {"title": "Hey Bulldog", "album": "Yellow Submarine", "songwriters": "Lennon", "vocals": "Lennon, with McCartney", "year": "1968", "notes": ""},
"heyjude": {"title": "Hey Jude", "album": "UK: 1967–1970 US: Hey Jude", "songwriters": "McCartney", "vocals": "McCartney", "year": "1968", "notes": ""},
"hippyhippyshake": {"title": "Hippy Hippy Shake", "album": "Live at the BBC", "songwriters": "Chan Romero", "vocals": "McCartney", "year": "1963", "notes": "Cover"},
"holdmetight": {"title": "Hold Me Tight", "album": "UK: With the Beatles US: Meet the Beatles!", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney", "year": "1963", "notes": ""},
"honeydont": {"title": "Honey Don't", "album": "UK: Beatles for Sale US: Beatles '65", "songwriters": "Carl Perkins", "vocals": "Starr", "year": "1964", "notes": "Cover"},
"honeypie": {"title": "Honey Pie", "album": "The Beatles", "songwriters": "McCartney", "vocals": "McCartney", "year": "1968", "notes": ""},
"howdoyoudoit": {"title": "How Do You Do It?", "album": "Anthology 1", "songwriters": "Mitch Murray", "vocals": "Lennon", "year": "1962", "notes": "Cover"},
"iamthewalrus": {"title": "I Am the Walrus", "album": "Magical Mystery Tour", "songwriters": "Lennon", "vocals": "Lennon", "year": "1967", "notes": ""},
"icallyourname": {"title": "I Call Your Name", "album": "UK: \"Long Tall Sally\" EP US: The Beatles' Second Album", "songwriters": "Lennon", "vocals": "Lennon", "year": "1964", "notes": "First release by Billy J Kramer with the Dakotas\n(July 1963)"},
"idontwanttospoiltheparty": {"title": "I Don't Want to Spoil the Party", "album": "UK: Beatles for Sale US: Beatles VI", "songwriters": "Lennon", "vocals": "Lennon, with McCartney", "year": "1964", "notes": ""},
"ifeelfine": {"title": "I Feel Fine", "album": "UK: A Collection of Beatles Oldies US: Beatles '65", "songwriters": "Lennon", "vocals": "Lennon", "year": "1964", "notes": "Non-album single"},
"iforgottoremembertoforget": {"title": "I Forgot to Remember to Forget", "album": "Live at the BBC", "songwriters": "Stan Kesler and Charlie Feathers", "vocals": "Harrison", "year": "1964", "notes": "Cover"},
"igotawoman": {"title": "I Got a Woman", "album": "Live at the BBC", "songwriters": "Ray Charles", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"igottofindmybaby": {"title": "I Got to Find My Baby", "album": "Live at the BBC", "songwriters": "Chuck Berry", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"ijustdontunderstand": {"title": "I Just Don't Understand", "album": "Live at the BBC", "songwriters": "Marijohn Wilkin\nKent Westberry", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"ilostmylittlegirl": {"title": "I Lost My Little Girl", "album": "", "songwriters": "McCartney", "vocals": "Lennon", "year": "1962", "notes": ""},
"imemine": {"title": "I Me Mine", "album": "Let It Be", "songwriters": "Harrison", "vocals": "Harrison", "year": "1970", "notes": ""},
"ineedyou": {"title": "I Need You", "album": "Help!", "songwriters": "Harrison", "vocals": "Harrison", "year": "1965", "notes": ""},
"isawherstandingthere": {"title": "I Saw Her Standing There", "album": "UK: Please Please Me US: Meet the Beatles!", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney, with Lennon", "year": "1963", "notes": ""},
"ishouldhaveknownbetter": {"title": "I Should Have Known Better", "album": "UK: A Hard Day's Night US: Hey Jude", "songwriters": "Lennon", "vocals": "Lennon", "year": "1964", "notes": ""},
"iwannabeyourman": {"title": "I Wanna Be Your Man", "album": "UK: With the Beatles US: Meet the Beatles!", "songwriters": "McCartney\n(with Lennon)", "vocals": "Starr", "year": "1963", "notes": "Written for the Rolling Stones"},
"iwantyoushessoheavy": {"title": "I Want You (She's So Heavy)", "album": "Abbey Road", "songwriters": "Lennon", "vocals": "Lennon", "year": "1969", "notes": ""},
"iwanttoholdyourhand": {"title": "I Want to Hold Your Hand", "album": "UK: A Collection of Beatles Oldies US: Meet the Beatles!", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon, McCartney", "year": "1963", "notes": ""},
"iwanttotellyou": {"title": "I Want to Tell You", "album": "Revolver", "songwriters": "Harrison", "vocals": "Harrison", "year": "1966", "notes": ""},
"iwill": {"title": "I Will", "album": "The Beatles", "songwriters": "McCartney", "vocals": "McCartney", "year": "1968", "notes": ""},
"illbeback": {"title": "I'll Be Back", "album": "UK: A Hard Day's Night US: Beatles '65", "songwriters": "Lennon", "vocals": "Lennon and McCartney)", "year": "1964", "notes": ""},
"illbeonmyway": {"title": "I'll Be on My Way", "album": "Live at the BBC", "songwriters": "McCartney", "vocals": "Lennon", "year": "1963", "notes": "Single by Billy J Kramer with the Dakotas\n(April 1963)"},
"illcryinstead": {"title": "I'll Cry Instead", "album": "UK: A Hard Day's Night US: Something New", "songwriters": "Lennon", "vocals": "Lennon", "year": "1964", "notes": ""},
"illfollowthesun": {"title": "I'll Follow the Sun", "album": "UK: Beatles for Sale US: Beatles '65", "songwriters": "McCartney", "vocals": "McCartney, with Lennon", "year": "1964", "notes": ""},
"illgetyou": {"title": "I'll Get You", "album": "UK: Past Masters Volume 1 US: The Beatles' Second Album", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon, with McCartney", "year": "1963", "notes": "Non-album single\nB-side of \"She Loves You\""},
"imdown": {"title": "I'm Down", "album": "Rock 'n' Roll Music", "songwriters": "McCartney", "vocals": "McCartney", "year": "1965", "notes": "Non-album single\nB-side of \"Help!\""},
"imgonnasitrightdownandcryoveryou": {"title": "I'm Gonna Sit Right Down and Cry (Over You)", "album": "Live at the BBC", "songwriters": "Joe Thomas\nHoward Biggs", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"imhappyjusttodancewithyou": {"title": "I'm Happy Just to Dance with You", "album": "UK: A Hard Day's Night US: Something New", "songwriters": "Lennon\nMcCartney", "vocals": "Harrison", "year": "1964", "notes": ""},
"iminlove": {"title": "I'm In Love", "album": "The Beatles Bootleg Recordings 1963", "songwriters": "Lennon", "vocals": "Lennon", "year": "1963", "notes": "Written for The Fourmost\n(single released November 1963)"},
"imlookingthroughyou": {"title": "I'm Looking Through You", "album": "Rubber Soul", "songwriters": "McCartney", "vocals": "McCartney, with Lennon", "year": "1965", "notes": ""},
"imonlysleeping": {"title": "I'm Only Sleeping", "album": "UK: Revolver US: Yesterday and Today", "songwriters": "Lennon", "vocals": "Lennon", "year": "1966", "notes": ""},
"imsotired": {"title": "I'm So Tired", "album": "The Beatles", "songwriters": "Lennon", "vocals": "Lennon", "year": "1968", "notes": ""},
"imtalkingaboutyou": {"title": "I'm Talking About You", "album": "Live! at the Star-Club in Hamburg, Germany; 1962", "songwriters": "Chuck Berry", "vocals": "Lennon", "year": "1962", "notes": "Cover"},
"imaloser": {"title": "I'm a Loser", "album": "UK: Beatles for Sale US: Beatles '65", "songwriters": "Lennon", "vocals": "Lennon", "year": "1964", "notes": ""},
"ivegotafeeling": {"title": "I've Got a Feeling", "album": "Let It Be", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney, with Lennon", "year": "1969", "notes": ""},
"ivejustseenaface": {"title": "I've Just Seen a Face", "album": "UK: Help! US: Rubber Soul", "songwriters": "McCartney", "vocals": "McCartney", "year": "1965", "notes": ""},
"ififell": {"title": "If I Fell", "album": "UK: A Hard Day's Night US: Something New", "songwriters": "Lennon", "vocals": "Lennon, with McCartney", "year": "1964", "notes": ""},
"ifineededsomeone": {"title": "If I Needed Someone", "album": "UK: Rubber Soul US: Yesterday and Today", "songwriters": "Harrison", "vocals": "Harrison", "year": "1965", "notes": ""},
"ifyouvegottrouble": {"title": "If You've Got Trouble", "album": "Anthology 2", "songwriters": "Lennon\nMcCartney", "vocals": "Starr", "year": "1965", "notes": ""},
"inmylife": {"title": "In My Life", "album": "Rubber Soul", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon", "year": "1965", "notes": ""},
"inspiteofallthedanger": {"title": "In Spite of All the Danger", "album": "Anthology 1", "songwriters": "McCartney and Harrison", "vocals": "Lennon", "year": "1958", "notes": ""},
"itwontbelong": {"title": "It Won't Be Long", "album": "UK: With the Beatles US: Meet the Beatles!", "songwriters": "Lennon\n(with McCartney)", "vocals": "Lennon", "year": "1963", "notes": ""},
"itsalltoomuch": {"title": "It's All Too Much", "album": "Yellow Submarine", "songwriters": "Harrison", "vocals": "Harrison", "year": "1967", "notes": ""},
"itsonlylove": {"title": "It's Only Love", "album": "UK: Help! US: Rubber Soul", "songwriters": "Lennon", "vocals": "Lennon", "year": "1965", "notes": ""},
"jazzpianosong": {"title": "Jazz Piano Song", "album": "Let it Be film", "songwriters": "McCartney\nStarr", "vocals": "McCartney", "year": "1969", "notes": ""},
"jessiesdream": {"title": "Jessie's Dream", "album": "Magical Mystery Tour", "songwriters": "Lennon, McCartney, Harrison, Starr", "vocals": "Instrumental", "year": "1967", "notes": ""},
"johnnybgoode": {"title": "Johnny B. Goode", "album": "Live at the BBC", "songwriters": "Chuck Berry", "vocals": "Lennon", "year": "1964", "notes": "Cover"},
"julia": {"title": "Julia", "album": "The Beatles", "songwriters": "Lennon", "vocals": "Lennon", "year": "1968", "notes": ""},
"junk": {"title": "Junk", "album": "Anthology 3", "songwriters": "McCartney", "vocals": "McCartney", "year": "1968", "notes": ""},
"kansascityheyheyheyhey": {"title": "Kansas City/Hey-Hey-Hey-Hey!", "album": "UK: Beatles for Sale US: Beatles VI", "songwriters": "Jerry Leiber and Mike Stoller/Little Richard", "vocals": "McCartney", "year": "1964", "notes": "Cover"},
"keepyourhandsoffmybaby": {"title": "Keep Your Hands Off My Baby", "album": "Live at the BBC", "songwriters": "Gerry Goffin\nCarole King", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"kommgibmirdeinehand": {"title": "Komm, gib mir deine Hand", "album": "UK: Rarities US: Something New", "songwriters": "Lennon\nMcCartney\nJean Nicolas\nHeinz Hellmer", "vocals": "Lennon, McCartney", "year": "1964", "notes": "Non-album single\nGerman version of \"I Want to Hold Your Hand\""},
"ladymadonna": {"title": "Lady Madonna", "album": "UK: 1967-1970 US: Hey Jude", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney", "year": "1968", "notes": "Non-album single"},
"leavemykittenalone": {"title": "Leave My Kitten Alone", "album": "Anthology 1", "songwriters": "Little Willie John\nTitus Turner\nJames McDougall", "vocals": "Lennon", "year": "1964", "notes": "Cover"},
"lendmeyourcomb": {"title": "Lend Me Your Comb", "album": "Anthology 1", "songwriters": "Kay Twomey\nFred Wise\nBen Weisman", "vocals": "Lennon, McCartney", "year": "1963", "notes": "Cover"},
"letitbe": {"title": "Let It Be", "album": "Let It Be", "songwriters": "McCartney", "vocals": "McCartney", "year": "1969", "notes": ""},
"likedreamersdo": {"title": "Like Dreamers Do", "album": "Anthology 1", "songwriters": "McCartney", "vocals": "McCartney", "year": "1962", "notes": "Recorded by The Applejacks"},
"littlechild": {"title": "Little Child", "album": "UK: With the Beatles US: Meet the Beatles!", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon, McCartney", "year": "1963", "notes": ""},
"lonesometearsinmyeyes": {"title": "Lonesome Tears in My Eyes", "album": "Live at the BBC", "songwriters": "Johnny Burnette\nDorsey Burnette\nPaul Burlison\nAl Mortimer", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"longtallsally": {"title": "Long Tall Sally", "album": "UK: Long Tall Sally EP US: The Beatles' Second Album", "songwriters": "Robert \"Bumps\" Blackwell\nEnotris Johnson\nLittle Richard", "vocals": "McCartney", "year": "1964", "notes": "Non-album single\nCover"},
"longlonglong": {"title": "Long, Long, Long", "album": "The Beatles", "songwriters": "Harrison", "vocals": "Harrison", "year": "1968", "notes": ""},
"lookingglass": {"title": "Looking Glass", "album": "", "songwriters": "McCartney", "vocals": "McCartney", "year": "1962", "notes": ""},
"lovemedo": {"title": "Love Me Do", "album": "UK: Please Please Me US: The Early Beatles", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney, with Lennon", "year": "1962", "notes": "featuring Andy White on drums"},
"loveyouto": {"title": "Love You To", "album": "Revolver", "songwriters": "Harrison", "vocals": "Harrison", "year": "1966", "notes": ""},
"loveoftheloved": {"title": "Love of the Loved", "album": "", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney", "year": "1962", "notes": "Single by Cilla Black\n(September 1963)"},
"lovelyrita": {"title": "Lovely Rita", "album": "Sgt. Pepper's Lonely Hearts Club Band", "songwriters": "McCartney", "vocals": "McCartney", "year": "1967", "notes": ""},
"lucille": {"title": "Lucille", "album": "Live at the BBC", "songwriters": "Little Richard\nAlbert Collins", "vocals": "McCartney", "year": "1963", "notes": "Cover"},
"lucyintheskywithdiamonds": {"title": "Lucy in the Sky with Diamonds", "album": "Sgt. Pepper's Lonely Hearts Club Band", "songwriters": "Lennon", "vocals": "Lennon", "year": "1967", "notes": ""},
"madman": {"title": "Madman", "album": "N/A", "songwriters": "Lennon", "vocals": "Lennon", "year": "1969", "notes": "From Get Back/Let It Be sessions"},
"maggiemae": {"title": "Maggie Mae", "album": "Let It Be", "songwriters": "Traditional, arr. Lennon, McCartney\nHarrison, Starr", "vocals": "Lennon, with McCartney", "year": "1969", "notes": "Cover"},
"magicalmysterytour": {"title": "Magical Mystery Tour", "album": "Magical Mystery Tour", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney, with Lennon", "year": "1967", "notes": ""},
"mailmanbringmenomoreblues": {"title": "Mailman, Bring Me No More Blues", "album": "Anthology 3", "songwriters": "Ruth Roberts\nBill Katz\nStanley Clayton", "vocals": "Lennon", "year": "1969", "notes": "Cover"},
"marthamydear": {"title": "Martha My Dear", "album": "The Beatles", "songwriters": "McCartney", "vocals": "McCartney", "year": "1968", "notes": ""},
"matchbox": {"title": "Matchbox", "album": "UK: \"Long Tall Sally\" EP US: Something New", "songwriters": "Carl Perkins\nBlind Lemon Jefferson", "vocals": "Starr", "year": "1964", "notes": "Cover"},
"maxwellssilverhammer": {"title": "Maxwell's Silver Hammer", "album": "Abbey Road", "songwriters": "McCartney[56]", "vocals": "McCartney", "year": "1969", "notes": ""},
"meanmrmustard": {"title": "Mean Mr. Mustard", "album": "Abbey Road", "songwriters": "Lennon[58]", "vocals": "Lennon, with McCartney", "year": "1969", "notes": ""},
"memphistennessee": {"title": "Memphis, Tennessee", "album": "Live at the BBC", "songwriters": "Chuck Berry", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"michelle": {"title": "Michelle", "album": "Rubber Soul", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney", "year": "1965", "notes": ""},
"misery": {"title": "Misery", "album": "UK: Please Please Me US: Introducing… The Beatles", "songwriters": "Lennon\n(with McCartney)", "vocals": "Lennon and McCartney", "year": "1963", "notes": ""},
"moneythatswhatiwant": {"title": "Money (That's What I Want)", "album": "UK: With the Beatles US: The Beatles Second Album", "songwriters": "Berry Gordy\nJanie Bradford", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"moonlightbay": {"title": "Moonlight Bay", "album": "Anthology 1", "songwriters": "Percy Wenrich\nEdward Madden", "vocals": "Lennon, McCartney, Harrison, Eric Morecambe, Ernie Wise", "year": "1963", "notes": "Performed on the Morecambe and Wise Show in 2/12/63"},
"mothernaturesson": {"title": "Mother Nature's Son", "album": "The Beatles", "songwriters": "McCartney", "vocals": "McCartney", "year": "1968", "notes": ""},
"mrmoonlight": {"title": "Mr. Moonlight", "album": "UK: Beatles for Sale US: Beatles '65", "songwriters": "Roy Lee Johnson", "vocals": "Lennon", "year": "1964", "notes": "Cover"},
"noreply": {"title": "No Reply", "album": "UK: Beatles for Sale US: Beatles '65", "songwriters": "Lennon\n(with McCartney)", "vocals": "Lennon, with McCartney", "year": "1964", "notes": ""},
"norwegianwoodthisbirdhasflown": {"title": "Norwegian Wood (This Bird Has Flown)", "album": "Rubber Soul", "songwriters": "Lennon\n(with McCartney)", "vocals": "Lennon", "year": "1965", "notes": ""},
"notguilty": {"title": "Not Guilty", "album": "Anthology 3", "songwriters": "Harrison", "vocals": "Harrison", "year": "1968", "notes": ""},
"notasecondtime": {"title": "Not a Second Time", "album": "UK: With the Beatles US: Meet the Beatles!", "songwriters": "Lennon", "vocals": "Lennon", "year": "1963", "notes": ""},
"nothinshakinbuttheleavesonthetrees": {"title": "Nothin' Shakin' (But the Leaves on the Trees)", "album": "Live at the BBC", "songwriters": "Eddie Fontaine", "vocals": "Harrison", "year": "1963", "notes": "Cover"},
"nowhereman": {"title": "Nowhere Man", "album": "UK: Rubber Soul US: Yesterday and Today", "songwriters": "Lennon\n(with McCartney)", "vocals": "Lennon, with McCartney and Harrison", "year": "1965", "notes": ""},
"obladioblada": {"title": "Ob-La-Di, Ob-La-Da", "album": "The Beatles", "songwriters": "McCartney", "vocals": "McCartney", "year": "1968", "notes": ""},
"octopussgarden": {"title": "Octopus's Garden", "album": "Abbey Road", "songwriters": "Starkey[c]", "vocals": "Starr", "year": "1969", "notes": ""},
"ohdarling": {"title": "Oh! Darling", "album": "Abbey Road", "songwriters": "McCartney[32]", "vocals": "McCartney", "year": "1969", "notes": ""},
"oldbrownshoe": {"title": "Old Brown Shoe", "album": "UK: 1967–1970 US: Hey Jude", "songwriters": "Harrison", "vocals": "Harrison", "year": "1969", "notes": "Non-album single\nB-side of \"The Ballad of John and Yoko\""},
"oneafter": {"title": "One After 909", "album": "Let It Be", "songwriters": "Lennon", "vocals": "Lennon, with McCartney", "year": "1969", "notes": ""},
"oneandoneistwo": {"title": "One and One Is Two", "album": "", "songwriters": "McCartney", "vocals": "McCartney", "year": "1964", "notes": "Single by The Strangers with Mike Shannon\n(May 1964)"},
"onlyanorthernsong": {"title": "Only a Northern Song", "album": "Yellow Submarine", "songwriters": "Harrison", "vocals": "Harrison", "year": "1967", "notes": ""},
"oohmysoul": {"title": "Ooh! My Soul", "album": "Live at the BBC", "songwriters": "Little Richard", "vocals": "McCartney", "year": "1963", "notes": "Cover"},
"psiloveyou": {"title": "P.S. I Love You", "album": "UK: Please Please Me US: The Early Beatles", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney", "year": "1962", "notes": ""},
"paperbackwriter": {"title": "Paperback Writer", "album": "UK: A Collection of Beatles Oldies US: Hey Jude", "songwriters": "McCartney", "vocals": "McCartney", "year": "1966", "notes": "Non-album single"},
"pennylane": {"title": "Penny Lane", "album": "Magical Mystery Tour", "songwriters": "McCartney", "vocals": "McCartney", "year": "1966", "notes": "Double A-side single\nwith \"Strawberry Fields Forever\""},
"piggies": {"title": "Piggies", "album": "The Beatles", "songwriters": "Harrison", "vocals": "Harrison", "year": "1968", "notes": ""},
"pleasemrpostman": {"title": "Please Mr. Postman", "album": "UK: With the Beatles US: The Beatles' Second Album", "songwriters": "Georgia Dobbins\nWilliam Garrett\nBrian Holland\nRobert Bateman\nFreddie Gorman", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"pleasepleaseme": {"title": "Please Please Me", "album": "UK: Please Please Me US: The Early Beatles", "songwriters": "Lennon", "vocals": "Lennon and McCartney", "year": "1962", "notes": "Single"},
"polythenepam": {"title": "Polythene Pam", "album": "Abbey Road", "songwriters": "Lennon", "vocals": "Lennon", "year": "1969", "notes": ""},
"rain": {"title": "Rain", "album": "UK: Rarities US: Hey Jude", "songwriters": "Lennon", "vocals": "Lennon", "year": "1966", "notes": "Non-album single\nB-side to \"Paperback Writer\""},
"reallove": {"title": "Real Love", "album": "Anthology 2", "songwriters": "Lennon", "vocals": "Lennon", "year": "1980", "notes": ""},
"revolution": {"title": "Revolution", "album": "UK: 1967-1970 US: Hey Jude", "songwriters": "Lennon", "vocals": "Lennon", "year": "1968", "notes": "Non-album single\nB-side to \"Hey Jude\""},
"revolution": {"title": "Revolution 1", "album": "The Beatles", "songwriters": "Lennon", "vocals": "Lennon", "year": "1968", "notes": ""},
"revolution": {"title": "Revolution 9", "album": "The Beatles", "songwriters": "Lennon\n(with Ono and Harrison)", "vocals": "Sound Collage", "year": "1968", "notes": ""},
"ripitupshakerattleandrollbluesuedeshoes": {"title": "Rip It Up / Shake, Rattle, and Roll / Blue Suede Shoes", "album": "Anthology 3", "songwriters": "Robert Blackwell, John Marascalco (\"Rip It Up\")\nCharles Calhoun(\"Shake, Rattle, and Roll\")\nCarl Perkins (\"Blue Suede Shoes\")", "vocals": "Lennon, McCartney", "year": "1969", "notes": "Cover"},
"rockandrollmusic": {"title": "Rock and Roll Music", "album": "UK: Beatles for Sale US: Beatles '65", "songwriters": "Chuck Berry", "vocals": "Lennon", "year": "1964", "notes": "Cover"},
"rockyraccoon": {"title": "Rocky Raccoon", "album": "The Beatles", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney", "year": "1968", "notes": ""},
"rolloverbeethoven": {"title": "Roll Over Beethoven", "album": "UK: With the Beatles US: The Beatles' Second Album", "songwriters": "Chuck Berry", "vocals": "Harrison", "year": "1963", "notes": "Cover"},
"runforyourlife": {"title": "Run for Your Life", "album": "Rubber Soul", "songwriters": "Lennon\n(with McCartney)", "vocals": "Lennon", "year": "1965", "notes": ""},
"savoytruffle": {"title": "Savoy Truffle", "album": "The Beatles", "songwriters": "Harrison", "vocals": "Harrison", "year": "1968", "notes": ""},
"searchin": {"title": "Searchin'", "album": "Anthology 1", "songwriters": "Jerry Leiber and Mike Stoller", "vocals": "McCartney", "year": "1962", "notes": "Cover"},
"septemberintherain": {"title": "September in the Rain", "album": "", "songwriters": "Al Dubin\nHarry Warren", "vocals": "McCartney", "year": "1962", "notes": "Cover"},
"sexysadie": {"title": "Sexy Sadie", "album": "The Beatles", "songwriters": "Lennon", "vocals": "Lennon", "year": "1968", "notes": ""},
"sgtpepperslonelyheartsclubband": {"title": "Sgt. Pepper's Lonely Hearts Club Band", "album": "Sgt. Pepper's Lonely Hearts Club Band", "songwriters": "McCartney", "vocals": "McCartney, with Lennon, Harrison and Starr", "year": "1967", "notes": ""},
"sgtpepperslonelyheartsclubbandreprise": {"title": "Sgt. Pepper's Lonely Hearts Club Band (Reprise)", "album": "Sgt. Pepper's Lonely Hearts Club Band", "songwriters": "McCartney", "vocals": "McCartney, Lennon, Harrison, Starr", "year": "1967", "notes": ""},
"shakininthesixties": {"title": "Shakin' in the Sixties", "album": "Unreleased", "songwriters": "Lennon", "vocals": "Lennon", "year": "1969", "notes": ""},
"shecameinthroughthebathroomwindow": {"title": "She Came in Through the Bathroom Window", "album": "Abbey Road", "songwriters": "McCartney", "vocals": "McCartney", "year": "1969", "notes": ""},
"shelovesyou": {"title": "She Loves You", "album": "UK: A Collection of Beatles Oldies US: The Beatles Second Album", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon, McCartney", "year": "1963", "notes": "Non-album single"},
"shesaidshesaid": {"title": "She Said She Said", "album": "Revolver", "songwriters": "Lennon", "vocals": "Lennon", "year": "1966", "notes": ""},
"shesleavinghome": {"title": "She's Leaving Home", "album": "Sgt. Pepper's Lonely Hearts Club Band", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney, with Lennon", "year": "1967", "notes": ""},
"shesawoman": {"title": "She's a Woman", "album": "UK: Rarities US: Beatles '65", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney", "year": "1964", "notes": "Non-album single\nB-side to \"I Feel Fine\""},
"shout": {"title": "Shout", "album": "Anthology 1", "songwriters": "Rudolph Isley\nRonald Isley\nO'Kelly Isley Jr.", "vocals": "Lennon, McCartney, Harrison, Starr", "year": "1964", "notes": "Cover"},
"sieliebtdich": {"title": "Sie liebt dich", "album": "UK: Rarities US: Rarities", "songwriters": "Lennon\nMcCartney\nJean Nicolas\nLee Montogue", "vocals": "Lennon, McCartney", "year": "1964", "notes": "Non-album single\nGerman version of \"She Loves You\""},
"slowdown": {"title": "Slow Down", "album": "UK: \"Long Tall Sally\" EP US: Something New", "songwriters": "Larry Williams", "vocals": "Lennon", "year": "1964", "notes": "Non-album single\nB-side of \"Matchbox\"\nCover"},
"sohowcomenoonelovesme": {"title": "So How Come (No One Loves Me)", "album": "Live at the BBC", "songwriters": "Felice and Boudleaux Bryant", "vocals": "Harrison", "year": "1963", "notes": "Cover"},
"soldieroflovelaydownyourarms": {"title": "Soldier of Love (Lay Down Your Arms)", "album": "Live at the BBC", "songwriters": "Buzz Cason\nTony Moon", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"someotherguy": {"title": "Some Other Guy", "album": "Live at the BBC", "songwriters": "Jerry Leiber and Mike Stoller\nRichie Barrett", "vocals": "Lennon, McCartney", "year": "1963", "notes": "Cover"},
"something": {"title": "Something", "album": "Abbey Road", "songwriters": "Harrison", "vocals": "Harrison", "year": "1969", "notes": "Double A-side single\nwith \"Come Together\""},
"sourmilksea": {"title": "Sour Milk Sea", "album": "Unreleased", "songwriters": "Harrison", "vocals": "Harrison", "year": "1968", "notes": "White Album\"\" outtake"},
"stepinsidelovelosparanoias": {"title": "Step Inside Love/Los Paranoias", "album": "Anthology 3", "songwriters": "McCartney (\"Step Inside Love\")\nLennon–McCartney\nHarrison–Starr (\"Los Paranoias\")", "vocals": "McCartney", "year": "1968", "notes": "\"Step Inside Love\" was recorded by Cilla Black\n(1968)"},
"strawberryfieldsforever": {"title": "Strawberry Fields Forever", "album": "Magical Mystery Tour", "songwriters": "Lennon", "vocals": "Lennon", "year": "1966", "notes": "Double A-side single\n(with \"Penny Lane\")"},
"sunking": {"title": "Sun King", "album": "Abbey Road", "songwriters": "Lennon", "vocals": "Lennon, with McCartney and Harrison", "year": "1969", "notes": ""},
"suretofallinlovewithyou": {"title": "Sure to Fall (in Love with You)", "album": "Live at the BBC", "songwriters": "Carl Perkins\nQuinton Claunch\nBill Cantrell", "vocals": "McCartney", "year": "1963", "notes": "Cover"},
"sweetlittlesixteen": {"title": "Sweet Little Sixteen", "album": "Live at the BBC", "songwriters": "Chuck Berry", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"takegoodcareofmybaby": {"title": "Take Good Care of My Baby", "album": "", "songwriters": "Gerry Goffin\nCarole King", "vocals": "Harrison", "year": "1962", "notes": "Cover"},
"takingatriptocarolina": {"title": "Taking a Trip to Carolina", "album": "Let It Be... Naked - Fly on the Wall bonus disc", "songwriters": "Starr", "vocals": "Starr", "year": "1969", "notes": ""},
"taxman": {"title": "Taxman", "album": "Revolver", "songwriters": "Harrison", "vocals": "Harrison, with Lennon and McCartney", "year": "1966", "notes": "McCartney plays guitar solo"},
"teddyboy": {"title": "Teddy Boy", "album": "Anthology 3", "songwriters": "McCartney", "vocals": "McCartney", "year": "1969", "notes": "\"Let It Be\" outtake"},
"tellmewhatyousee": {"title": "Tell Me What You See", "album": "UK: Help! US: Beatles VI", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney, with Lennon", "year": "1965", "notes": ""},
"tellmewhy": {"title": "Tell Me Why", "album": "UK: A Hard Day's Night US: Something New", "songwriters": "Lennon", "vocals": "Lennon", "year": "1964", "notes": ""},
"thankyougirl": {"title": "Thank You Girl", "album": "UK: Rarities US: The Beatles Second Album", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon, McCartney", "year": "1963", "notes": "Non-album single\nB-side of \"From Me To You\""},
"thatmeansalot": {"title": "That Means a Lot", "album": "Anthology 2", "songwriters": "McCartney", "vocals": "McCartney", "year": "1965", "notes": "Recorded by P.J. Proby\n(1965)"},
"thatllbetheday": {"title": "That'll Be the Day", "album": "Anthology 1", "songwriters": "Jerry Allison\nBuddy Holly\nNorman Petty", "vocals": "Lennon", "year": "1958", "notes": "Cover"},
"thatsallrightmama": {"title": "That’s All Right (Mama)", "album": "Live at the BBC", "songwriters": "Arthur Crudup", "vocals": "McCartney", "year": "1963", "notes": "Cover"},
"theballadofjohnandyoko": {"title": "The Ballad of John and Yoko", "album": "UK: 1967–1970 US: Hey Jude", "songwriters": "Lennon", "vocals": "Lennon, with McCartney", "year": "1969", "notes": ""},
"thecontinuingstoryofbungalowbill": {"title": "The Continuing Story of Bungalow Bill", "album": "The Beatles", "songwriters": "Lennon", "vocals": "Lennon", "year": "1968", "notes": ""},
"theend": {"title": "The End", "album": "Abbey Road", "songwriters": "McCartney", "vocals": "McCartney", "year": "1969", "notes": ""},
"thefoolonthehill": {"title": "The Fool on the Hill", "album": "Magical Mystery Tour", "songwriters": "McCartney", "vocals": "McCartney", "year": "1967", "notes": ""},
"thehoneymoonsong": {"title": "The Honeymoon Song", "album": "Live at the BBC", "songwriters": "Mikis Theodorakis\nSansom", "vocals": "McCartney", "year": "1963", "notes": "Cover"},
"theinnerlight": {"title": "The Inner Light", "album": "UK: Rarities US: Rarities", "songwriters": "Harrison", "vocals": "Harrison", "year": "1968", "notes": "Non-album single\nB-side of \"Lady Madonna\""},
"thelongandwindingroad": {"title": "The Long and Winding Road", "album": "Let It Be", "songwriters": "McCartney", "vocals": "McCartney", "year": "1969", "notes": ""},
"thenightbefore": {"title": "The Night Before", "album": "Help!", "songwriters": "McCartney", "vocals": "McCartney", "year": "1965", "notes": ""},
"thesheikofaraby": {"title": "The Sheik of Araby", "album": "Anthology 1", "songwriters": "Harry B. Smith\nFrancis Wheeler\nTed Snyder", "vocals": "Harrison", "year": "1962", "notes": "Cover"},
"theword": {"title": "The Word", "album": "Rubber Soul", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon, with McCartney and Harrison", "year": "1965", "notes": ""},
"theresaplace": {"title": "There's a Place", "album": "UK: Please Please Me US: Rarities", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon, McCartney", "year": "1963", "notes": ""},
"thingswesaidtoday": {"title": "Things We Said Today", "album": "UK: A Hard Day's Night US: Something New", "songwriters": "McCartney", "vocals": "McCartney", "year": "1964", "notes": ""},
"thinkforyourself": {"title": "Think for Yourself", "album": "Rubber Soul", "songwriters": "Harrison", "vocals": "Harrison", "year": "1965", "notes": ""},
"thisboy": {"title": "This Boy", "album": "UK: Rarities US: Meet the Beatles!", "songwriters": "Lennon", "vocals": "Lennon, with McCartney and Harrison", "year": "1963", "notes": "Non-album single\nB-side of \"I Want To Hold Your Hand\""},
"threecoolcats": {"title": "Three Cool Cats", "album": "Anthology 1", "songwriters": "Jerry Leiber and Mike Stoller", "vocals": "Harrison", "year": "1962", "notes": "Cover"},
"tickettoride": {"title": "Ticket to Ride", "album": "Help!", "songwriters": "Lennon", "vocals": "Lennon, with McCartney", "year": "1965", "notes": ""},
"tilltherewasyou": {"title": "Till There Was You", "album": "UK: With the Beatles US: Meet the Beatles!", "songwriters": "Meredith Willson", "vocals": "McCartney", "year": "1963", "notes": "Cover"},
"tipofmytongue": {"title": "Tip of My Tongue", "album": "Unreleased", "songwriters": "Lennon\nMcCartney", "vocals": "Lennon, McCartney", "year": "", "notes": "Recorded by Tommy Quickly\n(Released in 1963)"},
"toknowheristoloveher": {"title": "To Know Her is to Love Her", "album": "Live at the BBC", "songwriters": "Phil Spector", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"tomorrowneverknows": {"title": "Tomorrow Never Knows", "album": "Revolver", "songwriters": "Lennon", "vocals": "Lennon", "year": "1966", "notes": ""},
"toomuchmonkeybusiness": {"title": "Too Much Monkey Business", "album": "Live at the BBC", "songwriters": "Chuck Berry", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"twistandshout": {"title": "Twist and Shout", "album": "UK: Please Please Me US: The Early Beatles", "songwriters": "Phil Medley\nBert Berns", "vocals": "Lennon", "year": "1963", "notes": "Cover"},
"twoofus": {"title": "Two of Us", "album": "Let It Be", "songwriters": "McCartney", "vocals": "McCartney, with Lennon", "year": "1969", "notes": ""},
"wait": {"title": "Wait", "album": "Rubber Soul", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney and Lennon", "year": "1965", "notes": ""},
"watchingrainbows": {"title": "Watching Rainbows", "album": "", "songwriters": "Lennon\nand McCartney", "vocals": "Lennon", "year": "1969", "notes": ""},
"wecanworkitout": {"title": "We Can Work It Out", "album": "UK: A Collection of Beatles Oldies US: Yesterday and Today", "songwriters": "McCartney\n(with Lennon)", "vocals": "McCartney, with Lennon", "year": "1965", "notes": "Non-album single\nDouble A-side with \"Day Tripper\""},
"whatgoeson": {"title": "What Goes On", "album": "UK: Rubber Soul US: Yesterday and Today", "songwriters": "Lennon\nMcCartney\nStarkey[d]", "vocals": "Starr", "year": "1965", "notes": ""},
"whatyouredoing": {"title": "What You're Doing", "album": "UK: Beatles for Sale US: Beatles VI", "songwriters": "McCartney", "vocals": "McCartney", "year": "1964", "notes": ""},
"whatsthenewmaryjane": {"title": "What's The New Mary Jane", "album": "Anthology 3", "songwriters": "Lennon", "vocals": "Lennon", "year": "1968", "notes": "\"White Album\" outtake"},
"whenigethome": {"title": "When I Get Home", "album": "UK: A Hard Day's Night US: Something New", "songwriters": "Lennon", "vocals": "Lennon", "year": "1964", "notes": ""},
"whenimsixtyfour": {"title": "When I'm Sixty-Four", "album": "Sgt. Pepper's Lonely Hearts Club Band", "songwriters": "McCartney", "vocals": "McCartney", "year": "1966", "notes": ""},
"whilemyguitargentlyweeps": {"title": "While My Guitar Gently Weeps", "album": "The Beatles", "songwriters": "Harrison", "vocals": "Harrison", "year": "1968", "notes": "Eric Clapton plays lead guitar\n(uncredited)"},
"whydontwedoitintheroad": {"title": "Why Don't We Do It in the Road?", "album": "The Beatles", "songwriters": "McCartney", "vocals": "McCartney", "year": "1968", "notes": ""},
"wildhoneypie": {"title": "Wild Honey Pie", "album": "The Beatles", "songwriters": "McCartney", "vocals": "McCartney", "year": "1968", "notes": ""},
"withalittlehelpfrommyfriends": {"title": "With a Little Help from My Friends", "album": "Sgt. Pepper's Lonely Hearts Club Band", "songwriters": "Lennon\nMcCartney", "vocals": "Starr, with Lennon and McCartney", "year": "1967", "notes": ""},
"withinyouwithoutyou": {"title": "Within You Without You", "album": "Sgt. Pepper's Lonely Hearts Club Band", "songwriters": "Lennon", "vocals": "Lennon", "year": "1967", "notes": ""},
"woman": {"title": "Woman", "album": "Let It Be film", "songwriters": "McCartney (as Bernard Webb)", "vocals": "McCartney", "year": "1965", "notes": "Single by Peter and Gordon\n(January 1966)"},
"wordsoflove": {"title": "Words of Love", "album": "UK: Beatles for Sale US: Beatles VI", "songwriters": "Buddy Holly", "vocals": "Lennon, McCartney", "year": "1964", "notes": "Cover"},
"yellowsubmarine": {"title": "Yellow Submarine", "album": "Revolver", "songwriters": "McCartney\n(with Lennon)", "vocals": "Starr", "year": "1966", "notes": ""},
"yerblues": {"title": "Yer Blues", "album": "The Beatles", "songwriters": "Lennon", "vocals": "Lennon", "year": "1968", "notes": ""},
"yesitis": {"title": "Yes It Is", "album": "UK: Rarities US: Beatles VI", "songwriters": "Lennon", "vocals": "Lennon, McCartney and Harrison", "year": "1965", "notes": "Non-album single\nB-side of \"Ticket to Ride\""},
"yesterday": {"title": "Yesterday", "album": "UK: Help! US: Yesterday and Today", "songwriters": "McCartney", "vocals": "McCartney", "year": "1965", "notes": ""},
"youcantdothat": {"title": "You Can't Do That", "album": "UK: A Hard Day's Night US: The Beatles Second Album", "songwriters": "Lennon", "vocals": "Lennon", "year": "1964", "notes": ""},
"youknowmynamelookupthenumber": {"title": "You Know My Name (Look Up the Number)", "album": "UK: Rarities US: Rarities", "songwriters": "Lennon\n(with McCartney)", "vocals": "Lennon, McCartney", "year": "1967", "notes": "Non-album single\nB-side of \"Let It Be\""},
"youknowwhattodo": {"title": "You Know What to Do", "album": "Anthology 1", "songwriters": "Harrison", "vocals": "Harrison", "year": "1964", "notes": ""},
"youlikemetoomuch": {"title": "You Like Me Too Much", "album": "UK: Help! US: Beatles VI", "songwriters": "Harrison", "vocals": "Harrison", "year": "1965", "notes": ""},
"younevergivemeyourmoney": {"title": "You Never Give Me Your Money", "album": "Abbey Road", "songwriters": "McCartney[61]", "vocals": "McCartney", "year": "1969", "notes": ""},
"youwontseeme": {"title": "You Won't See Me", "album": "Rubber Soul", "songwriters": "McCartney", "vocals": "McCartney", "year": "1965", "notes": ""},
"youllbemine": {"title": "You'll Be Mine", "album": "Anthology 1", "songwriters": "Lennon\nMcCartney", "vocals": "McCartney", "year": "1960", "notes": ""},
"youregoingtolosethatgirl": {"title": "You're Going to Lose That Girl", "album": "Help!", "songwriters": "Lennon", "vocals": "Lennon", "year": "1965", "notes": ""},
"youvegottohideyourloveaway": {"title": "You've Got to Hide Your Love Away", "album": "Help!", "songwriters": "Lennon", "vocals": "Lennon", "year": "1965", "notes": ""},
"youvereallygotaholdonme": {"title": "You've Really Got a Hold on Me", "album": "UK: With the Beatles US: The Beatles Second Album", "songwriters": "Smokey Robinson", "vocals": "Lennon and Harrison", "year": "1963", "notes": "Cover"},
"youngblood": {"title": "Young Blood", "album": "Live at the BBC", "songwriters": "Jerry Leiber and Mike Stoller", "vocals": "Harrison", "year": "1963", "notes": "Cover"},
"yourmothershouldknow": {"title": "Your Mother Should Know", "album": "Magical Mystery Tour", "songwriters": "McCartney", "vocals": "McCartney", "year": "1967", "notes": ""},
}

main()
