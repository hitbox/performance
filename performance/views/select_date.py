import datetime as dt
import calendar
from calendar import Calendar

from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import render_template
from flask import url_for
from flask_login import login_required

from ..authorization import redirect_password_reset
from ..authorization import basic_check
from ..extensions import db
from ..utils import nextmonth
from ..utils import prevmonth

def select_date_blueprint(ReportClass, date_attr_name):
    select_date_bp = Blueprint('select_date', __name__)

    @select_date_bp.context_processor
    def inject():
        return {
            'makedate': dt.date,
            'month_names': calendar.month_name,
            'weekday_abbr': calendar.day_abbr,
        }

    @select_date_bp.route('/<int:year>/<int:month>')
    @basic_check
    def index(year, month):
        today = dt.date.today()
        firstweekday = current_app.config['FIRSTWEEKDAY']
        context = {
            'year': year,
            'month': month,
            'today': today,
            'calendar': Calendar(firstweekday),
        }
        context['prevyear'], context['prevmonth'] = prevmonth(year, month)
        context['nextyear'], context['nextmonth'] = nextmonth(year, month)
        date_attr = getattr(ReportClass, date_attr_name)
        reports = ReportClass.query.filter(
            db.func.extract('year', date_attr) == year,
            db.func.extract('month', date_attr) == month,
        ).all()
        context['reports'] = {getattr(report, date_attr_name):report for report in reports}
        return render_template('select_date.html', **context)

    @select_date_bp.route('/today')
    @basic_check
    def goto_today():
        today = dt.date.today()
        return redirect(url_for('.index', year=today.year, month=today.month))

    return select_date_bp
