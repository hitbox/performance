"""
Conveniences for `flask shell`.
"""

def root_context():
    import datetime as dt
    from pprint import pprint

    import sqlalchemy as sa
    import sqlalchemy_utils as sa_utils

    from .extensions import assets
    from .extensions import db
    from .extensions import htmlmin
    from .extensions import login_manager
    from .forms import LoginForm
    from .forms import UserForm
    from .utils import ppattr

    context = locals()
    # add all the database models
    for mapper in db.Model.registry.mappers:
        context[mapper.class_.__name__] = mapper.class_
    return context

def init_app(app):
    @app.shell_context_processor
    def shell_context_processor():
        """
        Add convenient things to the flask shell.
        """
        return root_context()
