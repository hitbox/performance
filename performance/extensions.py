import flask_assets as fa

from flask_htmlmin import HTMLMIN
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

class PrefixMiddleware:
    """
    For development, prefix url.
    """

    def __init__(self, app, prefix):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].lower().startswith(self.prefix.lower()):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            message = (
                "URL does not belong to the app."
                f" Expected prefix {self.prefix!r} "
                f" but got {environ['PATH_INFO']!r}".encode()
            )
            return [message]


assets = fa.Environment()
db = SQLAlchemy()
htmlmin = HTMLMIN()
login_manager = LoginManager()

def init_assets():
    """
    Register bundles for templates.
    """
    assets.register(
        'sitecss',
        fa.Bundle(
            'css/site.css',
            filters = 'cssmin',
            output = 'gen/site.css',
        )
    )
    assets.register(
        'screencss',
        fa.Bundle(
            'css/screen.css',
            'css/external/flatpickr.min.css',
            filters = 'cssmin',
            output = 'gen/screen.css',
        )
    )
    assets.register(
        'printcss',
        fa.Bundle(
            'css/print.css',
            filters = 'cssmin',
            output = 'gen/print.css',
        )
    )
    # javascript
    assets.register(
        'sitejs',
        fa.Bundle(
            'js/external/flatpickr.min.js',
            'js/site.js',
            filters = 'jsmin',
            output = 'gen/site.js',
        )
    )
    assets.register(
        'flighteditjs',
        fa.Bundle(
            'js/flight-edit.js',
            filters = 'jsmin',
            output = 'gen/flightedit.js',
        )
    )

def init_app(app):
    """
    Initialize extensions against application.
    """

    init_assets()

    assets.init_app(app)
    htmlmin.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    if app.env == 'development':
        app.wsgi_app = PrefixMiddleware(app.wsgi_app, app.config['PREFIX'])
