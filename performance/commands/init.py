from flask.cli import AppGroup

from ..extensions import db as db_ext

init_cli = AppGroup('init', help='Database commands')

@init_cli.command(help='Initialize database')
def db():
    """
    Create all models in the database and prompt to add an admin user.
    """
    # declare all the models by importing and get the user object
    db_ext.create_all()
