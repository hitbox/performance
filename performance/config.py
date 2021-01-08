from .exceptions import AppError

# required to be set to something truthy
REQUIRED_TRUTHY = [
    'SESSION_COOKIE_PATH',
    'REMEMBER_COOKIE_PATH',
    'PERFORMANCE_CONTROLLABLE',
    'JAVASCRIPT_INJECTION',
    'TITLE',
]

# just required to exist in config
REQUIRED_EXISTS = [
]

def exists_and_truthy(config, key):
    return key in config and config[key]

def raise_for_config(app):
    """
    Ensure necessary configuration
    """
    for key in REQUIRED_TRUTHY:
        if not exists_and_truthy(app.config, key):
            raise AppError(f'{key} must be configured and truthy true.')
    for key in REQUIRED_EXISTS:
        if key not in app.config:
            raise AppError(f'{key} must be configured.')

def configure_defaults(app):
    app.config.setdefault('PREFIX', '/')
    app.config.setdefault('TITLE', 'TITLE')
    # Used in templates for date formats.
    datefmt = app.config.setdefault('DATEFMT', '%d-%b-%y')
    timefmt = app.config.setdefault('TIMEFMT', '%H:%S')
    app.config.setdefault('DATETIMEFMT', datefmt + ' ' + timefmt)
    # Used in templates to specify how many dates around the current should be
    # shown in navigation.
    app.config.setdefault('DATESPREAD', 4)
    # calendar
    app.config.setdefault('FIRSTWEEKDAY', 0)
    # top navigation (endpoint, text)
    app.config.setdefault('TOPNAV', [])
    app.config.setdefault('TOPNAVDEV', [])

def init_app(app):
    """
    Validate configuration and set defaults.
    """
    app.config.from_envvar('PERFORMANCE_CONFIG')
    raise_for_config(app)
    configure_defaults(app)
