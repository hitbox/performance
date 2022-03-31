import click

from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template
from flask import url_for

from ..authorization import edit_schedule_check
from ..extensions import db
from ..models import FlightType
from ..models import ScheduledReport

from .pluggable import ListView

scheduled_report_bp = Blueprint('scheduled_report', __name__)

@scheduled_report_bp.before_request
@edit_schedule_check
def before_request():
    """
    Enforce user can edit schedules.
    """

@scheduled_report_bp.route('/')
def list():
    """
    List scheduled reports.
    """
    if current_app.config.get('SCHEDULED_REPORTS_ONLYONE'):
        scheduled_report = ScheduledReport.query.one()
        return redirect(url_for('.edit', id=scheduled_report.id))
    else:
        scheduled_reports = ScheduledReport.query.order_by(
            ScheduledReport.display_order
        ).all()
        context = dict(
            scheduled_reports = scheduled_reports,
        )
        template = 'scheduled_report/list_scheduled_reports.html'
        return render_template(template, **context)

@scheduled_report_bp.route('/<int:id>')
def edit(id):
    """
    Edit ScheduledReport.
    """
    scheduled_report = ScheduledReport.query.get_or_404(id)
    flight_types = FlightType.query.order_by(FlightType.report_order).all()
    context = dict(
        scheduled_report = scheduled_report,
        flight_types = flight_types,
    )
    template = 'scheduled_report/edit_scheduled_report.html'
    return render_template(template, **context)

## commands ##

@scheduled_report_bp.cli.command('add', help='Add scheduled report.')
@click.option('--name', prompt=True)
@click.option('--display-order', prompt=True, type=click.INT)
def add(name, display_order):
    """
    Add a scheduled report.
    """
    scheduled_report = ScheduledReport(name=name, display_order=display_order)
    db.session.add(scheduled_report)
    db.session.commit()
