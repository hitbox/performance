from .init import init_cli
from .user import user_cli

def init_app(app):
    """
    Initialize additional flask command line interfaces.
    """
    app.cli.add_command(init_cli)
    app.cli.add_command(user_cli)
