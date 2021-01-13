import datetime as dt
import inspect
import re

from pprint import pprint

def camelcase(s):
    """
    Convert snake_case to camelCase.
    """
    head, *parts = iter(s.split('_'))
    return head + ''.join(sub.title() for sub in parts)

def snakecase(s):
    """
    Convert camelCase to snake_case.
    """
    pattern = '(?!^)[A-Z]'
    def repl(match):
        return '_' + match.group()
    result = re.sub(pattern, repl, s).lower().replace('._', '.')
    return result

def exists_and_truthy(config, key):
    """
    key exists in config and evals to true
    """
    return key in config and config[key]

def ppattr(obj):
    """
    Pretty-print an objects attributes and values ignoring underscored and
    methods.
    """
    pprint({ key: getattr(obj,key)
             for key in dir(obj)
             if not (key.startswith('_')
                 or inspect.ismethod(getattr(obj, key))) })

def daterange(start, end, step=1):
    """
    Like range for dates.
    """
    d = start
    while d < end:
        yield d
        d += dt.timedelta(days=step)

def prevmonth(year, month):
    if month == 1:
        return (year - 1, 12)
    else:
        return (year, month - 1)

def nextmonth(year, month):
    if month == 12:
        return (year + 1, 1)
    else:
        return (year, month + 1)

def datesaround(date, spread, inclusive=False):
    """
    Yield dates around `date` a `spread` number of days around it.

    :param date: center date
    :param spread: date spread in days
    :param inclusive: true to include end date
    """
    inclusive = int(bool(inclusive))
    start = date - dt.timedelta(days=spread)
    end = date + dt.timedelta(days=spread+inclusive)
    return daterange(start, end)

def getattrdotted(obj, name, *default):
    "getattr with support for dotted access"
    keys = name.split('.')
    for key in keys[:-1]:
        obj = getattr(obj, key)
    return getattr(obj, keys[-1], *default)

def setattrdotted(obj, name, value):
    "setattr with support for dotted access"
    keys = name.split('.')
    for key in keys[:-1]:
        obj = getattr(obj, key)
    setattr(obj, keys[-1], value)

def datefromiso(s):
    """
    Assumes the full ISO date/time format
    """
    return None if not s else dt.date.fromisoformat(s[:10])

def int_or_none(value):
    return int(value) if value else None

def float_or_none(value):
    return float(value) if value else None

def str_or_none(value):
    return str(value) if value else None

def timefromiso(s):
    if not s or len(s) < 19:
        return None
    if re.search('\+\d\d:\d\d$', s):
        # when you str() the datetime fields, using DAO, they come with a
        # +00:00 at the end; slice that off
        s = s[:-6]
    return dt.time.fromisoformat(s[-8:])
