import re

_delaystring_re = re.compile(
    r'(?P<code>[a-zA-Z]{3})\s*\(?\s*(?P<minutes>[0-9]{,3}\s*)?\s*\)?')

def delaystring(text):
    """
    Parse human data entry into a list of pairs of strings and minutes.
    """
    if text is None:
        return []
    matches = [(code, int(minutes) if minutes else None)
               for code, minutes in _delaystring_re.findall(text)]
    return matches

def formatdelays(items):
    return ' '.join(code.upper() + (f'({minutes})' if minutes else '')
                    for code, minutes in items)
