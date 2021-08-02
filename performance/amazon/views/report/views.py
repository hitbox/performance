import sqlalchemy as sa

from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from performance.authorization import basic_check
from performance.authorization import edit_check
from performance.extensions import db

from performance.amazon.forms import ReportForm
from performance.amazon.models import Flight
from performance.amazon.models import Report
from performance.amazon.models import ScheduledReport

report_bp = Blueprint('report', __name__, template_folder='templates')

def get_performance_from(reports):
    """
    Return performance numbers (lanes, chargeable delays, and over-30 count).
    :param reports: list of reports.
    """
    lanes = sum(report.lanes() for report in reports)
    chargeable_delays = sum(len(report.chargeable_delays()) for report in reports)
    over30 = sum(len(report.over30()) for report in reports)
    result = dict(
        lanes = lanes,
        chargeable_delays = chargeable_delays,
        over30 = over30,
    )
    return result

def get_context(report):
    month_to_date = Report.query.filter(
        sa.func.date_part('year', Report.date) == report.date.year,
        sa.func.date_part('month', Report.date) == report.date.month,
        Report.date <= report.date,
    ).all()
    month_to_date = get_performance_from(month_to_date)

    quarter_to_date = Report.query.filter(
        sa.func.date_part('year', Report.date) == report.date.year,
        # quarter of a date calculation
        # (month - 1) // 3 + 1
        # sa.func.div postgres specific
        sa.func.div(
            sa.cast(
                sa.func.date_part('month', Report.date) - 1,
                sa.Integer),
            3) + 1 == (report.date.month - 1) // 3 + 1,
        Report.date <= report.date,
    ).all()
    #
    quarter_to_date = get_performance_from(quarter_to_date)
    # assumed best lanes for quarter is effectively quarter-to-date
    assumed_best_lanes_quarter_percent = None
    if report.performance_meta:
        best_lanes = report.performance_meta.assumed_best_lanes_quarter
        if best_lanes:
            assumed_best_lanes_quarter_percent = (best_lanes - quarter_to_date['chargeable_delays']) / best_lanes
            assumed_best_lanes_quarter_percent = assumed_best_lanes_quarter_percent
    #
    context = dict(
        report = report,
        month_to_date = month_to_date,
        quarter_to_date = quarter_to_date,
        assumed_best_lanes_quarter_percent = assumed_best_lanes_quarter_percent,
    )
    return context

@report_bp.route('/view/<int:id>')
@basic_check
def view_report(id):
    """
    View Report object.
    """
    report = Report.query.get_or_404(id)
    context = get_context(report)
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
        report = report,
    )
    return render_template('report/edit.html', **context)

@report_bp.route('/delete/<int:report_id>')
@edit_check
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    return redirect(url_for('select_date.goto_today'))

@report_bp.route('/create_from_schedule/<date:report_date>/<schedule_id>')
@edit_check
def create_report_from_schedule(report_date, schedule_id):
    scheduled_report = ScheduledReport.query.get_or_404(schedule_id)
    report = Report(
        date = report_date,
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

@report_bp.route('/new/<date:report_date>')
@edit_check
def prompt_new(report_date):
    """
    Prompt to create new report.
    """
    context = {
        'report_date': report_date,
        'scheduled_reports': ScheduledReport.query.all(),
    }
    return render_template('report/prompt_new.html', **context)
