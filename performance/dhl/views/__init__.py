import humanize
import werkzeug

from flask import current_app
from flask import flash
from flask import render_template
from flask import url_for

from ...views import select_date

from ..models import Report

from .flight import flight_bp
#from .import_excel import import_excel_bp
from .report.views import report_bp
from .scheduled_flight import scheduled_flight_bp
from .scheduled_report import scheduled_report_bp

def init_app(app):
    app.register_blueprint(flight_bp, url_prefix='/flight')
    #app.register_blueprint(import_excel_bp, url_prefix='/import_excel')
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(scheduled_flight_bp, url_prefix='/scheduled-flight')
    app.register_blueprint(scheduled_report_bp, url_prefix='/scheduled-report')

    select_date_bp = select_date.select_date_blueprint(Report, 'date')
    app.register_blueprint(select_date_bp, url_prefix='/select')
