"""
Conveniences for `flask shell`.
"""
from ..shell import root_context

# ensure all dhl sub-models are defined
from . import models

def init_app(app):
    @app.shell_context_processor
    def shell_context_processor():
        """
        Add convenient things to the flask shell.
        """
        context = root_context()
        return context
