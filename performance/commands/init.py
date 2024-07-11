from flask.cli import AppGroup

from ..extensions import db as db_ext

init_cli = AppGroup('init', help='Database commands')

@init_cli.command(help='Initialize database')
def db():
    """
    Create database tables.
    """
    db_ext.create_all()
