from collections import namedtuple

from flask import current_app

class Delay(namedtuple('Delay', ['code', 'minutes', 'cancelled'])):
    """
    A flight delay code, the minutes and if the code is cancelled.
    """

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
