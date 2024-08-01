import os
import pickle

import click
import sqlalchemy as sa

from performance import models
from performance import settings
from performance.extensions import db

from .blueprint import scheduled_report_bp

_default_scheduled_report_filename_format = (
    '{config.PERFORMANCE_REPORT_TITLE}'
    '_{scheduled_report.name}'
    '.{format}'
)

_known_export_formats = ['pickle']

scheduled_report_bp.cli.help = 'Scheduled reports utilities.'

def scheduled_report_from_dict(data):
    """
    Create ScheduledReport from data. The related ScheduledFlight objects are
    created if not found because there are probably duplicates in the export
    data.
    """
    scheduled_report = models.ScheduledReport.get_or_new_from_dict(data)
    return scheduled_report

@scheduled_report_bp.cli.command('list')
def list():
    """
    List scheduled reports names.
    """
    delete_query = (
        sa.select(models.ScheduledReport.name)
        .order_by(models.ScheduledReport.display_order)
    )
    result = db.session.scalars(delete_query)
    for name in result:
        click.echo(name)


@scheduled_report_bp.cli.command('delete')
@click.argument(
    'names',
    nargs = -1,
)
@click.option(
    '--yes',
    is_flag = True,
    help = 'Confirm delete all without prompt.',
)
def delete(names, yes):
    """
    Delete scheduled reports.
    """
    if not names:
        if not yes:
            yes = click.confirm(
                'Delete all scheduled reports and scheduled flights?')
        if not yes:
            return
        query = sa.select(models.ScheduledReport.name)
        names = db.session.execute(query).scalars().all()
    delete_query = (
        sa.delete(models.ScheduledReport).where(models.ScheduledReport.name.in_(names)))
    db.session.execute(delete_query)
    db.session.commit()
    for name in names:
        click.echo(f'Deleted {name}')


@scheduled_report_bp.cli.command(
    'export',
)
@click.argument(
    'scheduled_report_names',
    nargs = -1,
)
@click.option(
    '--format',
    type = click.Choice(_known_export_formats),
    show_default = True,
    default = _known_export_formats[0],
)
@click.option(
    '--output',
    default = _default_scheduled_report_filename_format,
    show_default = True,
    help = 'Format string for output filename.',
)
def export(scheduled_report_names, format, output):
    """
    Export a scheduled reports and their scheduled flights.
    """
    performance_report_title = settings.performance_report_title()
    if not scheduled_report_names:
        query = sa.select(models.ScheduledReport.name)
        scheduled_report_names = db.session.execute(query).scalars().all()

    fn_formatter = output.format
    for scheduled_report_name in scheduled_report_names:
        if not scheduled_report_name:
            # mistaken empty string names exist, skip them
            continue
        # get instance
        query = (
            sa.select(models.ScheduledReport)
            .where(
                models.ScheduledReport.name == scheduled_report_name,
            )
        )
        scheduled_report = db.session.scalars(query).one()
        # make filename
        fn_context = dict(
            format = format,
            config = settings.config_as_obj(),
            scheduled_report = scheduled_report,
        )
        fn = fn_formatter(**fn_context)
        # do export for format type
        if format == 'pickle':
            with open(fn, 'wb') as output_file:
                pickle.dump(scheduled_report.as_dict(), output_file)


@scheduled_report_bp.cli.command('import')
@click.argument(
    'source',
    nargs = -1,
)
@click.option(
    '--format',
    type = click.Choice(_known_export_formats),
    help = 'Export format of source file. Guess by extension if not given.',
)
def import_(source, format):
    """
    Import a scheduled report.
    """
    for source_fn in source:
        _, ext = os.path.splitext(source_fn)
        if ext.startswith('.pickle'):
            with open(source_fn, 'rb') as source_file:
                scheduled_report_data = pickle.load(source_file)
                scheduled_report = scheduled_report_from_dict(scheduled_report_data)
                db.session.add(scheduled_report)

    db.session.commit()
