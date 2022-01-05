import datetime

from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template
from flask import url_for

from .. import config
from ..authorization import basic_check
from ..extensions import db
from ..month import Month

config.require('FIRSTWEEKDAY', 'isint')

def select_date_blueprint(ReportClass, date_attr_name):
    """
    Return routes using configured ReportClass to compensate for differences
    between `performance.amazon` and `performance.dhl`.
    """
    # TODO: flatten. "plugging in" a specific model is no long needed.
    select_date_bp = Blueprint('select_date', __name__)

    @select_date_bp.route('/<int:year>/<int:month>')
    @basic_check
    def index(year, month):
        """
        Display a calendar with indication of existing reports and with links
        to the reports.
        """
        today = datetime.date.today()
        firstweekday = current_app.config['FIRSTWEEKDAY']
        monthobj = Month(year, month, firstweekday)
        # add useful report info to month days attribute
        date_attr = getattr(ReportClass, date_attr_name)
        reports = ReportClass.query.filter(
            db.func.extract('year', date_attr) == year,
            db.func.extract('month', date_attr) == month,
        ).all()
        report_dates = {report.date:report for report in reports}
        for day in monthobj.days:
            if day.date in report_dates:
                day.report = report_dates[day.date]
        context = dict(
            today = today,
            month = monthobj,
        )
        return render_template('select_date.html', **context)

    @select_date_bp.route('/today')
    @basic_check
    def goto_today():
        today = datetime.date.today()
        return redirect(url_for('.index', year=today.year, month=today.month))

    return select_date_bp
