import calendar as calendarlib
import datetime

from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template
from flask import url_for

from .. import config
from ..authorization import basic_check
from ..extensions import db
from ..models import AssumedBest
from ..models import Report
from ..month import Month

config.require('FIRSTWEEKDAY', 'isint')

select_date_bp = Blueprint('select_date', __name__)

@select_date_bp.before_request
@basic_check
def before_request():
    """
    basic_check for all requests
    """

@select_date_bp.route('/daily/<int:year>/<int:month>')
def calendar(year, month):
    """
    Display a calendar with indication of existing reports and with links
    to the reports.
    """
    today = datetime.date.today()
    firstweekday = current_app.config['FIRSTWEEKDAY']
    month_object = Month(year, month, firstweekday)
    # add useful report info to month days attribute
    reports = Report.query.filter(
        db.func.extract('year', Report.date) == year,
        db.func.extract('month', Report.date) == month,
    ).all()
    report_dates = {report.date: report for report in reports}
    for day in month_object.days:
        if day.date in report_dates:
            day.report = report_dates[day.date]
        else:
            day.report = None
    context = dict(
        today = today,
        month = month_object,
    )
    return render_template('select-date.html', **context)

@select_date_bp.route('/today')
def goto_today():
    """
    Redirect to current calendar.
    """
    today = datetime.date.today()
    return redirect(url_for('.calendar', year=today.year, month=today.month))

@select_date_bp.route('/monthly/<int:year>')
def monthly(year):
    """
    Yearly calendar to select a month.
    """
    existing_bests_query = db.select(
        AssumedBest,
    ).where(
        AssumedBest.year == year,
    )
    existing_bests = db.session.scalars(existing_bests_query).all()
    context = dict(
        AssumedBest = AssumedBest,
        calendarlib = calendarlib,
        existing_months = {best.month: best for best in existing_bests},
    )
    return render_template('select-month.html', **context)

@select_date_bp.route('/month')
def monthly_today():
    today = datetime.date.today()
    return redirect(url_for('.monthly', year=today.year))
