import click

from flask import Blueprint

from ..external import excel_schedule

external_bp = Blueprint('import', __name__)

@external_bp.route('/excel-schedule')
def import_excel_schedule():
    return 'excel'

@external_bp.cli.command('excel')
@click.argument('path', type=click.Path(exists=True))
def excel(path):
    """
    Import Excel Schedule file.
    """
    excel_schedule
