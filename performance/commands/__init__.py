from .init import init_cli

def init_app(app):
    """
    Initialize additional flask command line interfaces.
    """
    app.cli.add_command(init_cli)
