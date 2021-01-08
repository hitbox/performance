import calendar
import datetime

from .utils import nextmonth
from .utils import prevmonth

class Weekday:
    """
    Convenience class that provides useful attributes for a weekday.
    """

    def __init__(self, number):
        self.number = number
        self.name = calendar.day_name[self.number]
        self.abbr = calendar.day_abbr[self.number]
        self.shortabbr = self.abbr[:3]
        self.shortestabbr = self.abbr[:2]


class Day:
    """
    Convenience class that provides useful attributes for a day.
    """

    def __init__(self, number, _month):
        self.number = number
        self._month = _month
        self._date = None

    @property
    def date(self):
        if self._date is None and self.number:
            self._date = datetime.date(self._month.year, self._month.month, self.number)
        return self._date


class Month:
    """
    Convenience class that provides useful attributes for a month.
    """

    def __init__(self, year, month, firstweekday=0):
        self.year = year
        self.month = month
        self.name = calendar.month_name[self.month]
        self.abbr = calendar.month_abbr[self.month]
        self._cal = calendar.Calendar(firstweekday=firstweekday)
        self._days = None
        self._weekdays = None
        self._prevmonth = None
        self._nextmonth = None

    @property
    def weekdays(self):
        if self._weekdays is None:
            self._weekdays = list(map(Weekday, self._cal.iterweekdays()))
        return self._weekdays

    @property
    def days(self):
        if self._days is None:
            days = self._cal.itermonthdays(self.year, self.month)
            self._days = [Day(n, self) for n in days]
        return self._days

    @property
    def previous(self):
        if self._prevmonth is None:
            year, month = prevmonth(self.year, self.month)
            self._prevmonth = self.__class__(year, month)
        return self._prevmonth

    @property
    def next(self):
        if self._nextmonth is None:
            year, month = nextmonth(self.year, self.month)
            self._nextmonth = self.__class__(year, month)
        return self._nextmonth
