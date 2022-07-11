import datetime

from itertools import zip_longest

from flask import Flask

# ensure shared models defined
from . import models

from . import commands
from . import config
from . import converters
from . import extensions
from . import shell
from . import views

def create_app(silent_config=False):
    """
    Performance report Flask app.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_envvar('PERFORMANCE_CONFIG', silent=silent_config)
    config.raise_for_config(app)

    app.config.setdefault('LATE_GT', 0)
    app.config.setdefault('EARLY_LT', 0)
    # if diff minutes do not meet threshold, always show these delay codes
    # list of strings
    app.config.setdefault('ALWAYS_SHOW_DELAY_CODES', [])

    @app.context_processor
    def context_processor():
        """
        Application wide template injection.
        """
        context = dict(
            datetime = datetime,
            zip = zip,
            zip_longest = zip_longest,
            db = extensions.db,
        )
        return context

    commands.init_app(app)
    converters.init_app(app)
    extensions.init_app(app)
    shell.init_app(app)
    views.init_app(app)

    return app
