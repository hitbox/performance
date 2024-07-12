from . import constants
from .exceptions import PerformanceError

_required_registry = {}
_development_registry = {}

class ConfigError(PerformanceError):
    pass


class String:
    """
    Is string callable? With optional minimum length.
    """

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


def exists_and_truthy(config, key):
    """
    key exists in config and evals to true
    """
    return key in config and config[key]

def isint(value):
    """
    Is an integer?
    """
    return isinstance(value, int)

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

def validate_external(app):
    # external import/update config and their requirements
    external_keys = [
        constants.PERFORMANCE_EXTERNAL_IMPORT,
        constants.PERFORMANCE_EXTERNAL_UPDATE,
    ]
    required_for_external_import = [
        constants.PERFORMANCE_EXTERNAL_QUERY_CARRIER,
        constants.PERFORMANCE_EXTERNAL_QUERY_USAGE,
        constants.KG_CONVERSION_FACTOR,
    ]
    for external_key in external_keys:
        if not app.config.get(external_key, False):
            continue
        # external import enabled, other config required
        for dependency_key in required_for_external_import:
            if dependency_key not in app.config:
                raise ConfigError(
                    f'{dependency_key} required for {external_key}')

            value = app.config[dependency_key]
            if not value:
                raise ConfigError(
                    f'{dependency_key} must have a value')

def raise_for_config(app):
    """
    Main entry for app creation configuration validation.
    """
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
                        f' Expected {validator}')

    if app.debug:
        _raise_for_config(app, _development_registry, prefix='Development: ')
    _raise_for_config(app, _required_registry)

    validate_external(app)

# universal requirements
require_all(String(min=1), [
    'SESSION_COOKIE_PATH',
    'REMEMBER_COOKIE_PATH',
    constants.DATEFMT,
    constants.TIMEFMT,
    constants.PERFORMANCE_HEAD_TITLE,
    constants.PERFORMANCE_REPORT_TITLE,
])

require('PERFORMANCE_JAVASCRIPT_INJECTION', Dictionary())

require_all(List(is_populated=True), [
    constants.PERFORMANCE_CONTROLLABLE,
    constants.PERFORMANCE_LANES_FLIGHTTYPES,
])

require('PREFIX', String(min=1), is_development=True)
