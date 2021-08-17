import re

from collections import namedtuple

from flask import current_app

CANCELLED = 'XLD'

_delaystring_re = re.compile(
    r'(?P<code>[a-zA-Z]{3})'
    r'\s*\(?\s*'
    r'(?P<minutes>[0-9]{,3}\s*)'
    r'?\s*\)?')

class Delay(namedtuple('Delay', ['code', 'minutes', 'cancelled'])):

    def is_controllable(self, over_minutes):
        """
        The delay is controllable if the code is in PERFORMANCE_CONTROLLABLE
        app variable.
        :param over_minutes: further filter by minutes. this is ignored if code
                             is cancelled.
        """
        controllable_codes = current_app.config['PERFORMANCE_CONTROLLABLE']
        is_controllable = (
            # code is in configured controllable
            self.code in controllable_codes
            and (
                # is cancelled
                self.cancelled
                # or has minutes and they're over
                or (self.minutes and self.minutes > over_minutes))
        )
        return is_controllable

    def as_text(self):
        parts = []
        if self.cancelled:
            parts.append(CANCELLED)
        parts.append(self.code)
        if self.minutes:
            parts.append(str(self.minutes))
        return ' '.join(parts)


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
            if code == CANCELLED:
                # consume next match making cancelled=True
                for code, minutes in matches:
                    delay = Delay(code, minutes, True)
                    delays.append(delay)
                    break
                # what if cancelled is the last code?
            else:
                # take as non-cancelled code
                delay = Delay(code, minutes, False)
                delays.append(delay)

    return delays

def formatdelays(items):
    return ' '.join(code.upper() + (f'({minutes})' if minutes else '')
                    for code, minutes in items)
