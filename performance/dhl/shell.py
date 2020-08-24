"""
Conveniences for `flask shell`.
"""
# ensure all models are defined
from . import models

def init_app(app):
    @app.shell_context_processor
    def shell_context_processor():
        """
        Add convenient things to the flask shell.
        """
        import datetime as dt
        from pprint import pprint

        import sqlalchemy as sa
        import sqlalchemy_utils as sa_utils

        from ..extensions import assets
        from ..extensions import db
        from ..extensions import htmlmin
        from ..extensions import login_manager
        from ..forms import LoginForm
        from ..forms import UserForm

        context = locals()

        # add all the database models
        context.update(db.Model._decl_class_registry)

        return context
