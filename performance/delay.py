from collections import namedtuple

from flask import current_app

class LegacyDelay(namedtuple('Delay', ['code', 'minutes', 'is_cancelled'])):
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
                self.is_cancelled
                # or has minutes and they're over
                or (self.minutes and self.minutes > over_minutes))
        )
        return is_controllable

    def code_text(self):
        """
        The code part as showable.
        """
        from .parse import CANCELLED

        strings = []
        if self.is_cancelled and self.code != CANCELLED:
            strings.append(CANCELLED)
        if self.code:
            strings.append(self.code)
        text = ' '.join(strings)
        return text
