from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for

from ....authorization import basic_check
from ....authorization import edit_check
from ....extensions import db
from ....views.pluggable import ModelView
from ....views.pluggable import UpdateDeleteView

from ...forms import ReportForm
from ...models import Flight
from ...models import Operation
from ...models import Report
from ...models import ScheduledReport

report_bp = Blueprint('report', __name__, template_folder='templates')

report_bp.add_url_rule(
    '/edit/<int:id>',
    view_func = edit_check(
        UpdateDeleteView.as_view(
            'edit_report',
            ReportForm,
            model = Report,
            template = 'report/edit.html',
            instance_name = 'report',
        )))

report_bp.add_url_rule(
    '/view/<int:id>',
    view_func = basic_check(
        ModelView.as_view(
            'view_report',
            Report,
            'report/print.html',
            instance_name = 'report',
        )))

@report_bp.route('/create_blank_report/<date:report_date>')
@edit_check
def create_report_blank(report_date):
    """
    Create a new blank report.
    """
    report = Report(date=report_date)
    db.session.add(report)
    db.session.commit()
    return redirect(url_for('.view_report', id=report.id))

@report_bp.route('/add/<date:report_date>')
@edit_check
def create_report(report_date):
    """
    Create a new report.
    """
    report = Report(date=report_date)
    db.session.add(report)
    db.session.commit()
    return redirect(url_for('.view_report', id=report.id))

@report_bp.route('/new/<date:report_date>')
@edit_check
def prompt_new(report_date):
    # keep endpoint name the same as Amazon so that select_date will enter here.
    context = {
        'report_date': report_date,
        'scheduled_reports': ScheduledReport.query.all(),
    }
    return render_template('report/prompt_schedule.html', **context)

@report_bp.route('/new/<int:schedule_id>/<date:report_date>')
@edit_check
def prompt_operation(schedule_id, report_date):
    # keep endpoint name the same as Amazon so that select_date will enter here.
    context = {
        'report_date': report_date,
        'scheduled_report': ScheduledReport.query.get_or_404(schedule_id),
        'operations': Operation.query.all(),
    }
    return render_template('report/prompt_operation.html', **context)

@report_bp.route('/create_from_schedule/<date:report_date>/<int:schedule_id>/<int:operation_id>')
@edit_check
def create_report_from_schedule(report_date, schedule_id, operation_id):
    scheduled_report = ScheduledReport.query.get_or_404(schedule_id)
    operation = Operation.query.get_or_404(operation_id)
    report = Report(
        operation_date = report_date,
        operation = operation,
        flights = [
            Flight(
                flight_number = scheduled_flight.flight_number,
                leg = scheduled_flight.leg,
                tail_number = scheduled_flight.tail_number,
                weight = scheduled_flight.weight,
                comment = scheduled_flight.comment,
                origin_station = scheduled_flight.origin_station,
                origin_departure_estimated_date = scheduled_flight.origin_departure_estimated_date,
                origin_departure_estimated_time = scheduled_flight.origin_departure_estimated_time,
                destination_station = scheduled_flight.destination_station,
                destination_arrival_estimated_date = scheduled_flight.destination_arrival_estimated_date,
                destination_arrival_estimated_time = scheduled_flight.destination_arrival_estimated_time,
                flight_type = scheduled_flight.flight_type,
            )
            for scheduled_flight in scheduled_report.scheduled_flights
        ],
    )
    db.session.add(report)
    db.session.commit()
    return redirect(url_for('.edit_report', id=report.id))
