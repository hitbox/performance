from .business import business_cli
from .init import init_cli
from .mdb import mdb_cli

def init_app(app):
    """
    Initialize additional flask command line interfaces.
    """
    app.cli.add_command(business_cli)
    app.cli.add_command(init_cli)
    app.cli.add_command(mdb_cli)
