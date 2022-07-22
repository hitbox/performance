import datetime as dt
import math
import re

from flask import redirect
from flask import request
from flask import url_for

def get_thisurl():
    return url_for(request.endpoint, **request.view_args, **request.args)

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

def is_field_populated(form, name):
    field = getattr(form, name, None)
    return (
        hasattr(field, 'data')
        and getattr(field, 'data', None)
    )

def get_form_redirect(form):
    # putting this logic in one place
    # TODO: should check that url is safe
    # backendpoint, backviewargs? instead of full url?
    if (
        form.is_delete
        and is_field_populated(form, 'delete_url')
    ):
        return form.delete_url.data
    elif is_field_populated(form, 'backurl'):
        return redirect(form.backurl.data)

def sortfunc_by_type(obj):
    """
    Return function to sort 2-tuple items in an object according to the
    object's type.
    """
    if isinstance(obj, dict):
        def sortfunc(item):
            """
            Sort items in dictionary by values in same dict, or `math.inf` if missing.
            """
            name, field = item
            return obj.get(name, math.inf)

    elif isinstance(obj, list):
        def sortfunc(item):
            """
            Sort items in a list by index or `math.inf` if name is missing.
            """
            name, field = item
            if name in obj:
                return obj.index(name)
            else:
                return math.inf

    else:
         raise TypeError('Sorting by %r not supported', type(obj))

    return sortfunc
