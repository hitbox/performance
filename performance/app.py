from flask import Flask

from . import commands
from . import config
from . import converters
from . import extensions
from . import models
from . import shell
from . import views

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    config.init_app(app)

    commands.init_app(app)
    converters.init_app(app)
    extensions.init_app(app)
    shell.init_app(app)
    views.init_app(app)

    return app
