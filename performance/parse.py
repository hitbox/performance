import re

from collections import namedtuple

CANCELLED = 'XLD'

_delaystring_re = re.compile(
    r'(?P<code>[a-zA-Z]{3})'
    r'\s*\(?\s*'
    r'(?P<minutes>[0-9]{,3}\s*)'
    r'?\s*\)?')

Delay = namedtuple('Delay', ['code', 'minutes', 'cancelled'])

def delaystring(text):
    """
    Parse human data entry into a list of pairs of strings and minutes.
    """
    if text is None:
        return []
    matches = iter(
            (code, int(minutes) if minutes else None)
            for code, minutes in _delaystring_re.findall(text))

    codes = []
    for code, minutes in matches:
        if code == CANCELLED:
            for code, minutes in matches:
                delay = Delay(code, minutes, True)
                codes.append(delay)
                break
        else:
            delay = Delay(code, minutes, False)
            codes.append(delay)

    return codes

def formatdelays(items):
    return ' '.join(code.upper() + (f'({minutes})' if minutes else '')
                    for code, minutes in items)
