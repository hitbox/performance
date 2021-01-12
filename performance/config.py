from .exceptions import AppError

# required to be set to something truthy
REQUIRED_TRUTHY = [
    'SESSION_COOKIE_PATH',
    'REMEMBER_COOKIE_PATH',
    # list of stations to consider for calculating what delays were controllable:
    'PERFORMANCE_CONTROLLABLE',
    # <head><title>...
    'PERFORMANCE_HEAD_TITLE',
    # dict to inject into javascript through the templates:
    'PERFORMANCE_JAVASCRIPT_INJECTION',
    'PERFORMANCE_REPORT_DATEFMT',
    'PERFORMANCE_REPORT_TITLE',
]

REQUIRED_TRUTHY_IF_DEVELOPMENT = [
    'PREFIX',
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
    if app.env == 'development':
        for key in REQUIRED_TRUTHY_IF_DEVELOPMENT:
            if not exists_and_truthy(app.config, key):
                raise AppError(f'in development, {key} must be configured and'
                                ' truthy true.')
    for key in REQUIRED_EXISTS:
        if key not in app.config:
            raise AppError(f'{key} must be configured.')

def configure_defaults(app):
    app.config.setdefault('PREFIX', '/')
    # Used in templates for date formats.
    datefmt = app.config.setdefault('DATEFMT', '%d-%b-%y')
    timefmt = app.config.setdefault('TIMEFMT', '%H:%S')
    app.config.setdefault('DATETIMEFMT', datefmt + ' ' + timefmt)
    # Used in templates to specify how many dates around the current should be
    # shown in navigation.
    app.config.setdefault('DATESPREAD', 4)
    # calendar 0 is Monday and default, 6 is Sunday
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
