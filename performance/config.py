from .exceptions import AppError
from .utils import exists_and_truthy

_required_registry = {}
_development_registry = {}

class ConfigError(Exception):
    pass


def isint(value):
    "An integer"
    return isinstance(value, int)

class String:
    "Is string"

    def __init__(self, min=None):
        self.min = min

    def __str__(self):
        return self.__doc__

    def __call__(self, value):
        return (
            isinstance(value, str)
            and (self.min is None or len(value) >= self.min))


class List:

    def __init__(self, is_populated=False):
        self.is_populated = is_populated

    def __call__(self, value):
        return (
            isinstance(value, list)
            and (not self.is_populated or len(value) > 0))


class Dictionary:

    def __call__(self, value):
        return isinstance(value, dict)


def require(key, validator, is_development=False):
    if is_development:
        registry = _development_registry
    else:
        registry = _required_registry
    if key in registry:
        raise ConfigError('Key already exists, %r' % key)
    if isinstance(validator, str):
        # pluck from globals
        namespace = globals()
        if validator not in namespace:
            raise ConfigError('Invalid validator name, %r' % validator)
        validator = namespace[validator]
    registry[key] = validator

def require_all(validator, keys, is_development=False):
    for key in keys:
        require(key, validator, is_development=is_development)

def raise_for_config(app):
    def _raise_for_config(app, registry, prefix=''):
        for key, validator in registry.items():
            try:
                value = app.config[key]
            except KeyError:
                raise ConfigError(f'{prefix}Missing config key, {key!r}')
            else:
                if not validator(value):
                    raise ConfigError(
                        f'{prefix}Invalid config value {value!r} for {key!r}.'
                        f'Expected {validator}')
    if app.env == 'development':
        _raise_for_config(app, _development_registry, prefix='Development: ')
    _raise_for_config(app, _required_registry)

# universal requirements
require_all(String(min=1), [
    'SESSION_COOKIE_PATH',
    'REMEMBER_COOKIE_PATH',
    'DATEFMT',
    'TIMEFMT',
    'DATETIMEFMT',
    'PERFORMANCE_HEAD_TITLE',
    'PERFORMANCE_REPORT_DATEFMT',
    'PERFORMANCE_REPORT_TITLE',
])

require('PERFORMANCE_JAVASCRIPT_INJECTION', Dictionary())

require_all(List(is_populated=True), [
    'PERFORMANCE_CONTROLLABLE',
])

require('PREFIX', String(min=1), is_development=True)
