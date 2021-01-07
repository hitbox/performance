import click
import openpyxl

from flask import Blueprint

from ...external import excel_schedule

external_bp = Blueprint('import', __name__)

TYPEMAP = {
    # Calendar module days of week: 0 is Monday, 6 is Sunday.
    # The worksheet seems to have 1 is Mon., 7 is Sunday.
    'UTC\nDOW': lambda v: list(int(c) for c in str(v-1)),
}

@external_bp.cli.command('excel')
@click.argument('path', type=click.Path(exists=True))
def excel(path):
    excel_schedule
