import datetime

from flask import Flask

# ensure shared models defined
from . import models

from . import commands
from . import config
from . import converters
from . import extensions
from . import shell
from . import utils
from . import views

def setdefault_config(app):
    app.config.setdefault('LATE_GT', 0)
    app.config.setdefault('EARLY_LT', 0)
    # if diff minutes do not meet threshold, always show these delay codes
    # list of strings
    app.config.setdefault('ALWAYS_SHOW_DELAY_CODES', [])

    performance_stats = app.config.setdefault('PERFORMANCE_STATS', {})
    performance_stats.setdefault('lanes', True)
    performance_stats.setdefault('chargeable_delays', True)
    performance_stats.setdefault('delays_gt_30_count', True)
    performance_stats.setdefault('on_time_performance_gt_15', True)
    performance_stats.setdefault('on_time_performance_gt_30', True)

def ensure_metadata(app):
    # ensure that at least one object exists for metadata settings
    db = extensions.db
    with app.app_context():
        stmt = db.select(models.Performance)
        settings = db.session.scalars(stmt).one_or_none()
        if not settings:
            db.session.add(models.Performance())
            db.session.commit()

def init_app(app):
    """
    Initialize other things that need to initialize against the app.
    """
    commands.init_app(app)
    converters.init_app(app)
    extensions.init_app(app)
    shell.init_app(app)
    views.init_app(app)

def init_context_processor(app):
    """
    Add an application wide context for templates.
    """

    @app.context_processor
    def context_processor():
        """
        Application wide template injection.
        """
        context = dict(
            datetime = datetime,
            db = extensions.db,
            thisurl = utils.get_thisurl(),
            javascript_injection = {},
        )
        return context

def create_app(silent_config=False):
    """
    Performance report Flask app.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_envvar('PERFORMANCE_CONFIG', silent=silent_config)
    config.raise_for_config(app)
    setdefault_config(app)

    init_context_processor(app)
    init_app(app)
    ensure_metadata(app)

    return app
