from .mdb import mdb_cli

def init_app(app):
    """
    Initialize additional flask command line interfaces.
    """
    app.cli.add_command(mdb_cli)
    # NOTE
    # performance.dhl.views.report.views adds commands
