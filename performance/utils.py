import datetime as dt
import re

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

def massage_time(string):
    """
    Return string stripped of all but digits and left-padded with zeros to four places.
    """
    value = int(''.join(c for c in string if c.isdigit()))
    value = f'{value:04d}'
    return value

def quarter_of_date(date):
    """
    Return the quarter part of `date`.
    """
    return (date.month - 1) // 3 + 1

def diff_minutes(est_date, est_time, act_date, act_time):
    """
    If all truthy, calculate the difference in minute between estimated and
    actual dates and times.
    """
    if all([est_date, est_time, act_date, act_time]):
        est_dt = dt.datetime.combine(est_date, est_time)
        act_dt = dt.datetime.combine(act_date, act_time)
        a, b = sorted([est_dt, act_dt])
        minutes = int((b - a).total_seconds()) // 60
        if est_dt > act_dt:
            minutes *= -1
        return minutes
