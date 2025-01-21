import flask_assets as fa

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from .middleware import PrefixMiddleware

assets = fa.Environment()
db = SQLAlchemy()
login_manager = LoginManager()

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
    assets.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    if 'PREFIX' in app.config:
        app.wsgi_app = PrefixMiddleware(app.wsgi_app, app.config['PREFIX'])
