import click

from .views import report_bp

from performance.dhl import external_data
from performance.dhl import randomdata

@report_bp.cli.command('mkrandom')
@click.argument('date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.option('--commit/--no-commit')
def mkrandom(date, commit):
    """
    CLI create random report.
    """
    date = date.date()
    report = randomdata.random_report(date)
    db.session.add(report)
    if commit:
        db.session.commit()

@report_bp.cli.command('import-excel-schedule')
@click.argument('path', type=click.Path(exists=True))
def import_excel_schedule(path):
    """
    CLI import Excel schedule file.
    """
    data = external_data.excel_schedule.import_flights(path)
    #click.echo(data)
