import datetime

import sqlalchemy as sa

from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from ..authorization import basic_check
from ..authorization import edit_check
from ..extensions import db
from ..models import AssumedBest
from ..models import Flight
from ..models import Report
from ..models import ScheduledReport

report_bp = Blueprint('report', __name__)

def get_report_form_class():
    """
    Wrap in function to avoid the aggressiveness of wtforms_alchemy.
    """
    from ..forms import ReportForm
    return ReportForm

def get_performance_from(reports):
    """
    Return performance numbers (lanes, chargeable delays, and over-30 count).

    :param reports: list of reports.
    """
    lanes = [flight for report in reports for flight in report.lane_flights()]
    controllable_destination_delays_over15 = [
        delay
        for report in reports
        for delay
        in report.controllable_destination_delays(over_minutes=15)
    ]
    controllable_destination_delays_over30 = [
        delay
        for report in reports
        for delay
        in report.controllable_destination_delays(over_minutes=30)
    ]
    flights_with_controllable_destination_delays_over15 = [
        flight
        for report in reports
        for flight
        in report.flights_with_controllable_destination_delays(over_minutes=15)
    ]
    flights_with_controllable_destination_delays_over30 = [
        flight
        for report in reports
        for flight
        in report.flights_with_controllable_destination_delays(over_minutes=30)
    ]
    result = dict(
        lanes = lanes,
        controllable_destination_delays_over15
            = controllable_destination_delays_over15,
        controllable_destination_delays_over30
            = controllable_destination_delays_over30,
        flights_with_controllable_destination_delays_over15
            = flights_with_controllable_destination_delays_over15,
        flights_with_controllable_destination_delays_over30
            = flights_with_controllable_destination_delays_over30,
    )
    return result

def get_context(report):
    """
    Context data for viewing report.
    """
    month_to_date_reports = Report.query.filter(
        sa.func.date_part('year', Report.date) == report.date.year,
        sa.func.date_part('month', Report.date) == report.date.month,
        Report.date <= report.date,
    ).all()
    month_to_date = get_performance_from(month_to_date_reports)

    reports_quarter_to_date = Report.query.filter(
        Report.date <= report.date,
        sa.func.date_part('year', Report.date) == report.date.year,
        Report.date_quarter == report.date_quarter,
    ).all()

    # quarter to date assumed bests objects
    assumed_bests_qtd = [
        AssumedBest.query.filter(
            AssumedBest.year == report.date.year,
            AssumedBest.month == report.date.month,
        ).one_or_none()
        for report in reports_quarter_to_date
    ]
    assumed_bests_qtd = filter(None, assumed_bests_qtd)

    # quarter to date
    quarter_to_date = get_performance_from(reports_quarter_to_date)
    assumed_best = AssumedBest.query.filter(
        AssumedBest.year == report.date.year,
        AssumedBest.month == report.date.month,
    ).one_or_none()

    #
    context = dict(
        report = report,
        daily = dict(
            lanes = report.lane_flights(),
            controllable_destination_delays_over15
                = report.controllable_destination_delays(15),
            controllable_destination_delays_over30
                = report.controllable_destination_delays(30),
            flights_with_controllable_destination_delays_over15
                = report.flights_with_controllable_destination_delays(15),
            flights_with_controllable_destination_delays_over30
                = report.flights_with_controllable_destination_delays(30),
        ),
        month_to_date = month_to_date,
        quarter_to_date = quarter_to_date,
        assumed_best = assumed_best,
        assumed_bests_qtd = assumed_bests_qtd,
    )
    return context


@report_bp.route('/view/<date:report_date>')
@basic_check
def view_report_for_date(report_date):
    """
    Redirect from report date to id.
    """
    report = Report.query.filter(Report.date == report_date).one_or_none()

    if report is None:
        # Alert and redirect to new report
        if 'DATEFMT' in current_app.config:
            date_str = report_date.strftime(current_app.config['DATEFMT'])
        else:
            date_str = str(report_date)
        flash(f'{date_str} not found.', 'info')
        return redirect(url_for('.prompt_new', report_date=report_date))

    return redirect(url_for('.view_report', id=report.id))

@report_bp.route('/view/<int:id>', methods=['GET', 'POST'])
@basic_check
def view_report(id):
    """
    View Report object.
    """
    ReportForm = get_report_form_class()
    report = Report.query.get_or_404(id)
    form = ReportForm(obj=report)

    # only updating the comments (system detail)
    form.submit.label.text = 'Update System Detail'
    if form.validate_on_submit():
        report.system_detail = form.system_detail.data
        db.session.commit()
        return redirect(
            url_for(
                request.endpoint,
                _anchor = 'system-detail',
                **request.view_args
            )
        )

    context = get_context(report)
    context['prev_date'] = report.date - datetime.timedelta(days=1)
    context['next_date'] = report.date + datetime.timedelta(days=1)

    return render_template('report/print_with_edit.html', form=form, **context)

@report_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@edit_check
def edit_report(id):
    """
    Edit Report object.
    """
    ReportForm = get_report_form_class()
    report = Report.query.get_or_404(id)
    form = ReportForm(obj=report)
    assumed_best = AssumedBest.query.filter(
        AssumedBest.year == report.date.year,
        AssumedBest.month == report.date.month,
    ).one_or_none()

    if form.validate_on_submit():
        if hasattr(form, 'delete') and form.delete.data:
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
        assumed_best = assumed_best,
    )
    return render_template('report/edit.html', **context)

@report_bp.route('/delete/<int:report_id>')
@edit_check
def delete_report(report_id):
    """
    Delete Report
    """
    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    return redirect(url_for('select_date.goto_today'))

@report_bp.route('/create_from_schedule/<date:report_date>/<schedule_id>')
@edit_check
def create_report_from_schedule(report_date, schedule_id):
    """
    Create new report from scheduled report.
    """
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
    return redirect(url_for('.view_report', id=report.id))

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
    template = 'report/prompt_new.html'
    scheduled_reports_onlyone = current_app.config.get('SCHEDULED_REPORTS_ONLYONE', False)
    if scheduled_reports_onlyone:
        scheduled_report = ScheduledReport.query.one()
        context = dict(
            scheduled_report = scheduled_report
        )
    else:
        # all scheduled reports
        scheduled_reports = ScheduledReport.query.order_by(
                ScheduledReport.display_order
            ).all()
        context = dict(
            scheduled_reports = scheduled_reports,
        )
    return render_template(template, **context)
