import performance.app

# ensure models are defined
from . import models

from . import commands
from . import config
from . import shell
from . import views

def raise_for_values():
    from .models import Bound
    from .models import FlightType

def create_app():
    """
    DHL Flask Web App
    """
    app = performance.app.create_app()
    config.raise_config.raise_for_config(app)

    commands.init_app(app)
    shell.init_app(app)
    views.init_app(app)

    return app
