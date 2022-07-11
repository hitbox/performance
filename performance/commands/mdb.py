import click

from flask import current_app
from flask.cli import AppGroup

from performance.extensions import db
from performance.legacy.datamigration import Migrator
from performance.legacy.mdbreader import mdbreader

mdb_cli = AppGroup('mdb', help='Data commands')

@mdb_cli.command(help='Import Access database')
@click.argument('mdbpath', type=click.Path(exists=True))
@click.option('--commit', is_flag=True, show_default=True, help='Commit the changes.')
def pull(mdbpath, commit):
    migrator = Migrator(mdbpath)
    migrator.migrate()
    if commit:
        db.session.commit()
    else:
        click.echo('nothing committed')
