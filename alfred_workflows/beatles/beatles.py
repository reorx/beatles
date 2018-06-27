import sys
import datetime
import json
import time

DATE_FMT = '%Y-%m-%d'
DATETIME_FMT = '%Y-%m-%d %H:%M'
TIME_FMT = '%H:%M'


def new_item(uid, complete, title, v):
    d = {
        'uid': uid,
        'type': 'default',
        'title': title,
        'subtitle': v,
        'arg': v,
        'autocomplete': complete,
    }
    return d

l = []
now = datetime.datetime.now()

# date
v = now.strftime(DATE_FMT)
l.append(new_item('0date', 'date', 'Date', v))

# datetime
v = now.strftime(DATETIME_FMT)
l.append(new_item('1datetime', 'datetime', 'Datetime', v))

# time
v = now.strftime(TIME_FMT)
l.append(new_item('2time', 'time', 'Time', v))

# timestamp
v = str(int(time.time()))
l.append(new_item('3timestamp', 'timestamp', 'Timestamp', v))

out = {
    'items': l
}

sys.stdout.write(json.dumps(out))
