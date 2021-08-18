from performance.views import select_date

from performance.amazon.models import Report

from .assumed_best.views import assumed_best_bp
from .flight import flight_bp
from .report.views import report_bp
from .scheduled_flight import scheduled_flight_bp
from .scheduled_report import scheduled_report_bp
from .xhr import xhr_bp

def init_app(app):
    """
    Initialize Amazon views
    """
    app.register_blueprint(assumed_best_bp, url_prefix='/best')
    app.register_blueprint(flight_bp, url_prefix='/flight')
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(scheduled_flight_bp, url_prefix='/scheduled-flight')
    app.register_blueprint(scheduled_report_bp, url_prefix='/scheduled-report')
    app.register_blueprint(
        select_date.select_date_blueprint(Report, 'date'),
        url_prefix='/select')
    app.register_blueprint(xhr_bp, url_prefix='/xhr')
