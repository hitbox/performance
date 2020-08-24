from flask import Flask

import performance.app

from . import commands
from . import models
from . import shell
from . import views

def create_app():
    """
    DHL Flask Web App
    """
    app = performance.app.create_app()

    commands.init_app(app)
    shell.init_app(app)
    views.init_app(app)

    return app
