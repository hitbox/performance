import werkzeug

from flask import Flask
from flask import render_template

from . import commands
from . import config
from . import converters
from . import extensions
from . import models
from . import shell
from . import views

from .month import Weekday

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    config.init_app(app)

    commands.init_app(app)
    converters.init_app(app)
    extensions.init_app(app)
    shell.init_app(app)
    views.init_app(app)

    @app.errorhandler(werkzeug.exceptions.HTTPException)
    def error(e):
        """
        HTTP Error Code page to make everything styled consistently.
        """
        return (render_template('error.html', e=e), e.code)

    context = dict(
        weekday = {n:Weekday(n) for n in range(7)},
    )

    @app.context_processor
    def inject():
        return context

    return app
