from operator import attrgetter

from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from performance.authorization import basic_check
from performance.authorization import edit_check
from performance.extensions import db
from performance.models import FlightType
from performance.views.pluggable import ModelView
from performance.views.pluggable import UpdateDeleteView

from performance.dhl.forms import ReportForm
from performance.dhl.models import Bound
from performance.dhl.models import Flight
from performance.dhl.models import Operation
from performance.dhl.models import Report
from performance.dhl.models import ScheduledReport

report_bp = Blueprint('report', __name__, template_folder='templates')

def grouped_flights(report):
    # [((flight_type, bound), flights), ...]
    grouped = [
        ((flight_type, bound),
         sorted(
             (flight for flight in report.flights
              if flight.flight_type == flight_type and flight.bound == bound),
             key = attrgetter('flight_number')))
        for flight_type in FlightType.query.order_by(FlightType.report_order)
        for bound in Bound.query.order_by(Bound.report_order)
    ]
    return grouped

@report_bp.route('/view/<int:id>')
@basic_check
def view_report(id):
    """
    View DHL Report object.
    """
    report = Report.query.get_or_404(id)
    context = dict(
        report = report,
        grouped = grouped_flights(report),
    )
    return render_template('report/print.html', **context)

@report_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@edit_check
def edit_report(id):
    report = Report.query.get_or_404(id)
    form = ReportForm(obj=report)
    if form.validate_on_submit():
        if form.delete.data:
            db.session.delete(report)
        elif form.submit.data:
            form.populate_obj(report)
        db.session.commit()
        if hasattr(form, 'backurl') and form.backurl.data:
            return redirect(form.backurl.data)
    elif request.method == 'GET':
        form.submit.label.text = 'Update'
    context = dict(
        form = form,
        grouped = grouped_flights(report),
        report = report,
    )
    return render_template('report/edit.html', **context)

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

@report_bp.route('/prompt_new/<date:report_date>')
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
        date = report_date,
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


def trash():
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
