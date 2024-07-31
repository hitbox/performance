import pickle

import click
import sqlalchemy as sa

from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import request
from flask import url_for

from performance import settings
from performance.authorization import edit_schedule_check
from performance.extensions import db
from performance.forms import ScheduledFlightForm
from performance.forms import ScheduledReportForm
from performance.models import ScheduledReport
from performance.pluggable import FormListView

scheduled_report_bp = Blueprint('scheduled_report', __name__)

@scheduled_report_bp.before_request
@edit_schedule_check
def before_request():
    """
    Enforce user can edit schedules and redirect to the only schedule if
    configured for only one schedule.
    """
    # decorator enforces access
    if (
        'id' not in request.view_args
        and settings.scheduled_reports_onlyone()
    ):
        # throw exception for not one
        # redirect to the flights
        scheduled_report = ScheduledReport.query.one()
        return redirect(url_for('scheduled_flight.listform', scheduled_report_id=scheduled_report.id))

def context_processor():
    """
    Add a scheduled flight form instance the template can show on the same page.
    """
    form = ScheduledFlightForm()
    if 'id' in request.view_args:
        form.scheduled_report_id.data = request.view_args['id']
    return dict(new_scheduled_flight_form=form)

def response_for_delete(form):
    return redirect(url_for('scheduled_report.list'))

scheduled_report_bp.cli.help = 'Scheduled reports utilities.'

@scheduled_report_bp.cli.command('delete')
@click.argument('names', nargs=-1)
@click.option('--yes', is_flag=True, help='Confirm delete all without prompt.')
def cli_delete(names, yes):
    """
    Delete scheduled reports.
    """
    if not names:
        if not yes:
            yes = click.confirm(
                'Delete all scheduled reports and scheduled flights?')
        if not yes:
            return
        query = sa.select(ScheduledReport.name)
        names = db.session.execute(query).scalars().all()
    delete_query = (
        sa.delete(ScheduledReport).where(ScheduledReport.name.in_(names)))
    db.session.execute(delete_query)
    db.session.commit()
    click.echo('Deleted ' + ' '.join(f'"{name}"' for name in names))

_default_scheduled_report_filename_format = (
    '{config.PERFORMANCE_REPORT_TITLE}_{scheduled_report.name}.{format}'
)

_known_export_formats = ['pickle_dicts']

@scheduled_report_bp.cli.command('export')
@click.argument(
    'scheduled_report_names',
    nargs = -1,
)
@click.option(
    '--format',
    type = click.Choice(_known_export_formats),
    required = True,
)
@click.option(
    '--filename-format',
    default=_default_scheduled_report_filename_format,
    help = 'Format string for output filename.',
)
def cli_export(scheduled_report_names, format, filename_format):
    """
    Export a scheduled reports and their scheduled flights.
    """
    performance_report_title = settings.performance_report_title()
    if not scheduled_report_names:
        query = sa.select(ScheduledReport.name)
        scheduled_report_names = db.session.execute(query).scalars().all()

    fn_formatter = filename_format.format
    for scheduled_report_name in scheduled_report_names:
        # get instance
        query = (
            sa.select(ScheduledReport)
            .where(
                ScheduledReport.name == scheduled_report_name,
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
        if format == 'pickle_dicts':
            with open(fn, 'wb') as output_file:
                pickle.dump(scheduled_report.as_dict(), output_file)

@scheduled_report_bp.cli.command('import')
@click.argument(
    'source',
)
@click.option(
    '--format',
    type=click.Choice(_known_export_formats),
    help='Export format of file. Guess by extension if not given.',
)
def cli_import(source, format):
    """
    Import a scheduled report.
    """

view_func = FormListView.as_view(
    'list',
    instance_getter = ScheduledReport.noapp_get_or_404,
    pagination_getter = ScheduledReport.noapp_pagination,
    form_getter = ScheduledReportForm,
    form_submitter = ScheduledReportForm.standard_submit,
    response_for_delete = response_for_delete,
    template = 'scheduled-report/list-form.html',
    context_processor = context_processor,
)

scheduled_report_bp.add_url_rule(
    '/',
    view_func = view_func,
)

scheduled_report_bp.add_url_rule(
    '/<int:id>',
    view_func = view_func,
)
