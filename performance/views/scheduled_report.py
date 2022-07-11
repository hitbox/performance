import click

from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from ..authorization import admin_required
from ..authorization import edit_schedule_check
from ..extensions import db
from ..models import FlightType
from ..models import ScheduledReport

def scheduled_report_form_class():
    from performance.forms import ScheduledReportForm
    return ScheduledReportForm

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
        return redirect(url_for('.list_for_edit_scheduled_report_flights', id=scheduled_report.id))
    else:
        scheduled_reports = ScheduledReport.query.order_by(
            ScheduledReport.display_order
        ).all()
        context = dict(
            scheduled_reports = scheduled_reports,
        )
        template = 'scheduled_report/list-scheduled-reports.html'
        return render_template(template, **context)

@admin_required
@scheduled_report_bp.route('/add', methods=['GET', 'POST'])
def add_scheduled_report():
    """
    Add new scheduled report.
    """
    form_class = scheduled_report_form_class()
    form = form_class()
    del form.delete

    if form.validate_on_submit():
        new_instance = ScheduledReport()
        db.session.add(new_instance)
        form.populate_obj(new_instance)
        db.session.commit()
        db.session.flush()
        flash('New scheduled report added', 'success')
        endpoint = '.list_for_edit_scheduled_report_flights'
        return redirect(url_for(endpoint, id=new_instance.id))

    display_order_query = ScheduledReport.query.order_by(ScheduledReport.display_order)
    schedules = [schedule for schedule in display_order_query]

    # automatically fill display order field
    for schedule1, schedule2 in zip(schedules[:-1], schedules[1:]):
        if (schedule2.display_order - schedule1.display_order) > 1:
            flash(
                f'Available display order found between "{ schedule1.name }"'
                f' and "{ schedule2.name }"',
                'info'
            )
            form.display_order.data = schedule1.display_order + 1
            break
    else:
        display_orders = [schedule.display_order for schedule in schedules]
        form.display_order.data = 1 + max(display_orders, default=0)

    context = dict(
        form = form,
        schedules = schedules,
    )
    template = 'scheduled_report/edit-scheduled-report.html'
    return render_template(template, **context)

@scheduled_report_bp.route('/<int:id>')
def list_for_edit_scheduled_report_flights(id):
    """
    List of links to edit scheduled report flights and the report itself.
    """
    scheduled_report = ScheduledReport.query.get_or_404(id)
    flight_types = FlightType.query.order_by(FlightType.report_order).all()
    context = dict(
        scheduled_report = scheduled_report,
        flight_types = flight_types,
    )
    template = 'scheduled_report/list-for-edit-scheduled-report-flights.html'
    return render_template(template, **context)

@admin_required
@scheduled_report_bp.route('/schedule/<int:id>', methods=['GET', 'POST'])
def edit_scheduled_report(id):
    """
    Edit the direct attributes of a scheduled report.
    """
    form_class = scheduled_report_form_class()
    scheduled_report = ScheduledReport.query.get_or_404(id)
    form = form_class(obj=scheduled_report)

    if form.validate_on_submit():
        if form.delete.data:
            return redirect(url_for('.edit_scheduled_report_delete', id=id))
        else:
            form.populate_obj(scheduled_report)
            db.session.commit()
            endpoint = 'scheduled_report.list_for_edit_scheduled_report_flights'
            view_args = dict(id=scheduled_report.id)
            return redirect(url_for(endpoint, **view_args))

    context = dict(
        form = form,
        scheduled_report = scheduled_report,
    )
    template = 'scheduled_report/edit-scheduled-report.html'
    return render_template(template, **context)

@admin_required
@scheduled_report_bp.route('/schedule/delete/<int:id>', methods=['GET', 'POST'])
def edit_scheduled_report_delete(id):
    """
    Confirm deleting report.
    """
    form_class = scheduled_report_form_class()
    scheduled_report = ScheduledReport.query.get_or_404(id)
    form = form_class(obj=scheduled_report)
    del form.name
    del form.display_order
    del form.update

    if form.validate_on_submit():
        name = scheduled_report.name
        if form.delete.data:
            for flight in scheduled_report.scheduled_flights:
                db.session.delete(flight)
            db.session.delete(scheduled_report)
            db.session.commit()
            flash(f'Scheduled Report "{name}" deleted', 'warning')
            return redirect(url_for('.list'))

    if request.method != 'POST':
        # avoid flashing message on post
        flash(
            'This will delete the scheduled report and all associated scheduled'
            ' flights. Click delete again to confirm and delete.',
            'warning'
        )

    context = dict(
        form = form,
        scheduled_report = scheduled_report,
    )
    template = 'scheduled_report/edit-scheduled-report.html'
    return render_template(template, **context)

# CLI #

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
