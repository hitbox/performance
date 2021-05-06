from .exceptions import AppError
from .utils import exists_and_truthy

_registry = {}

class ConfigError(Exception):
    pass


def isint(value):
    "An integer"
    return isinstance(value, int)

def require(key, validate_func_name):
    if key in _registry:
        raise ConfigError('Key already exists, %r' % key)
    if validate_func_name not in globals():
        raise ConfigError('Invalid validator name, %r' % validate_func_name)
    validate_func = globals()[validate_func_name]
    _registry[key] = validate_func

def raise_for_config(app):
    for key, validator in _registry.items():
        try:
            value = app.config[key]
        except KeyError:
            raise ConfigError('Missing config key, %r' % key)
        else:
            if not validator(value):
                raise ConfigError(
                    'Invalid config value %r for %r. Expected %r'
                    % (value, key, validator.__doc__))

class ConfigValidator:
    """
    Ensure sane configuration as soon as possible.
    """

    def __init__(
            self,
            required_truthy,
            required_truthy_if_development,
            required_exists,
        ):
        """
        :param required_truthy: keys required to exist and have a truthy value.
        :param required_truthy_if_development: keys required truthy if
                app.env == 'development'.
        :param required_exists: keys required to exist.
        """
        self.required_truthy = required_truthy
        self.required_truthy_if_development = required_truthy_if_development
        self.required_exists = required_exists

    def raise_for_config(self, app):
        """
        Ensure necessary configuration
        """
        for key in self.required_truthy:
            if not exists_and_truthy(app.config, key):
                raise AppError(f'{key} must be configured and truthy true.')
        if app.env == 'development':
            for key in self.required_truthy_if_development:
                if not exists_and_truthy(app.config, key):
                    raise AppError(f'in development, {key} must be configured and'
                                    ' truthy true.')
        for key in self.required_exists:
            if key not in app.config:
                raise AppError(f'{key} must be configured.')


# required to be set to something truthy
REQUIRED_TRUTHY = [
    'FIRSTWEEKDAY',
    'SESSION_COOKIE_PATH',
    'REMEMBER_COOKIE_PATH',
    # used in templates and will blow up without these:
    'DATEFMT',
    'TIMEFMT',
    'DATETIMEFMT',
    # list of stations to consider for calculating what delays were controllable:
    'PERFORMANCE_CONTROLLABLE',
    # <head><title>...
    'PERFORMANCE_HEAD_TITLE',
    # dict to inject into javascript through the templates:
    'PERFORMANCE_JAVASCRIPT_INJECTION',
    'PERFORMANCE_REPORT_DATEFMT',
    'PERFORMANCE_REPORT_TITLE',
]

REQUIRED_TRUTHY_IF_DEVELOPMENT = ['PREFIX']

# just required to exist in config
REQUIRED_EXISTS = []

validate = ConfigValidator(
    REQUIRED_TRUTHY,
    REQUIRED_TRUTHY_IF_DEVELOPMENT,
    REQUIRED_EXISTS
)
