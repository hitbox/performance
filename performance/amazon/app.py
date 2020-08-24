from ..app import create_app as _create_app

from . import commands
from . import models
from . import views

def create_app():
    """
    Amazon Flask Web App
    """
    app = _create_app()

    commands.init_app(app)
    views.init_app(app)

    return app
