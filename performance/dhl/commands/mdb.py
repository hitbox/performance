import click

from flask.cli import AppGroup

from ...extensions import db

from ..external_data.mdb import Migrator

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
