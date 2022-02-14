import re

from .delay import Delay

CANCELLED = 'XLD'

_delaystring_re = re.compile(
    r'(?P<code>[a-zA-Z]{3})'
    r'\s*\(?\s*'
    r'(?P<minutes>[0-9]{,3}\s*)'
    r'?\s*\)?')

def delaystring(text):
    """
    Parse human data entry into a list of pairs of strings and minutes.
    """
    delays = []
    if text is not None:
        matches = iter(
                (code, int(minutes) if minutes else None)
                for code, minutes in _delaystring_re.findall(text))

        # interpret and convert into Delay objects.
        for code, minutes in matches:
            code = code.upper()
            if code == CANCELLED:
                # consume next match making cancelled=True
                for code, minutes in matches:
                    delay = Delay(code, minutes, True)
                    delays.append(delay)
                    break
                else:
                    delay = Delay(code, None, True)
                    delays.append(delay)
                # what if cancelled is the last code?
            else:
                # take as non-cancelled code
                delay = Delay(code, minutes, False)
                delays.append(delay)

    return delays

def formatdelays(delays):
    # similar: macros.html:render_delay
    # used by forms to populate inputs
    parts = []
    for code, minutes, cancelled in delays:
        if cancelled:
            s = 'XLD '
        else:
            s = ''
        s += code.upper()
        if minutes:
            s += f'({minutes})'
        parts.append(s)
    return ' '.join(parts)
