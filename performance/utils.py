import datetime as dt
import inspect
import re

from pprint import pprint

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
