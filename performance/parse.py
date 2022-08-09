import re

CANCELLED = 'XLD'
PLACEHOLDER_CODE = 'XXX'

_delaystring_re = re.compile(
    r'(?P<code>[a-zA-Z]{3})' # three letter codes, allowing lowercase in
    r'\s*' # optional whitespace
    r'\(?' # optional left parenthesis
    r'\s*' # optional whitespace
    r'(?P<minutes>[0-9]*)?' # optional number of minutes
    r'\s*' # optional whitespace
    r'\)?' # optional right parenthesis
)

def int_or_none(string):
    if string:
        return int(string)

def marshal(code, minutes):
    """
    Data types and validation for delay codes.
    """
    return (code.upper(), int_or_none(minutes))

def delaystring(text):
    """
    Parse human data entry into a list of pairs of strings and minutes.
    """
    matches = _delaystring_re.findall(text)
    matches = (marshal(code, minutes) for code, minutes in matches)
    # interpret and convert into Delay objects.
    delays = []
    for code, minutes in matches:
        is_cancelled = code == CANCELLED
        if is_cancelled:
            # consume next match overwriting namespace
            for code, minutes in matches:
                break
        data = dict(code=code, minutes=minutes, is_cancelled=is_cancelled)
        delays.append(data)
    return delays

def string_for_cancelled(is_cancelled):
    if is_cancelled:
        return CANCELLED + ' '
    else:
        return ''

def string_for_minutes(minutes):
    if minutes is not None:
        return f'({minutes})'
    else:
        return ''

def format_delay(code, minutes, is_cancelled):
    """
    Format a single flight delay from attributes.
    """
    code = code.upper()
    if is_cancelled and code == CANCELLED:
        return CANCELLED
    s = string_for_cancelled(is_cancelled)
    s += code
    s += string_for_minutes(minutes)
    return s

def get_delay_tuple(delay):
    """
    Ensure delay data is a properly ordered tuple for format_delay.
    """
    code = getattr(delay, 'code', delay['code'])
    minutes = getattr(delay, 'minutes', delay['minutes'])
    is_cancelled = getattr(delay, 'is_cancelled', delay['is_cancelled'])
    return (code, minutes, is_cancelled)

def formatdelays(delays):
    """
    Format delays as human readable string
    """
    # similar: macros.html:render_delay
    # used by forms to populate inputs
    parts = []
    for delay in delays:
        s = format_delay(*get_delay_tuple(delay))
        parts.append(s)
    return ' '.join(parts)
