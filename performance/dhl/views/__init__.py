from ...views import select_date

from ..models import Report

from .external import external_bp
from .flight import flight_bp
from .report.views import report_bp
from .scheduled_flight import scheduled_flight_bp
from .scheduled_report import scheduled_report_bp

select_date_bp = select_date.select_date_blueprint(Report, 'date')

def init_app(app):
    """
    Init DHL views.
    """
    app.register_blueprint(external_bp, url_prefix='/external')
    app.register_blueprint(flight_bp, url_prefix='/flight')
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(scheduled_flight_bp, url_prefix='/scheduled-flight')
    app.register_blueprint(scheduled_report_bp, url_prefix='/scheduled-report')
    app.register_blueprint(select_date_bp, url_prefix='/select')
