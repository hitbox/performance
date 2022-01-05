from flask import Flask

# ensure shared models defined
from . import models

from . import commands
from . import config
from . import converters
from . import extensions
from . import shell
from . import views

def create_app():
    """
    Performance report Flask app.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_envvar('PERFORMANCE_CONFIG')
    config.raise_for_config(app)

    commands.init_app(app)
    converters.init_app(app)
    extensions.init_app(app)
    shell.init_app(app)
    views.init_app(app)

    return app
