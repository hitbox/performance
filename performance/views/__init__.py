from flask import redirect
from flask import render_template
from flask import url_for
from werkzeug.exceptions import HTTPException

from ..authorization import redirect_password_reset

from .admin import admin_bp
from .assumed_best import assumed_best_bp
from .delay import delay_bp
from .flight import flight_bp
from .flight_type import flight_type_bp
from .performance_details import performance_details_bp
from .report import report_bp
from .scheduled_flight import scheduled_flight_bp
from .scheduled_report import scheduled_report_bp
from .select_date import select_date_bp
from .user import user_bp

def init_app(app):
    """
    Initialize views.
    """
    @app.errorhandler(HTTPException)
    def error(e):
        """
        HTTP Error Code page to make everything styled consistently.
        """
        return (render_template('error.html', e=e), e.code)

    @app.route('/')
    @redirect_password_reset
    def index():
        """
        Redirect root to today's calendar.
        """
        return redirect(url_for('select_date.goto_today'))

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(assumed_best_bp, url_prefix='/best')
    app.register_blueprint(delay_bp, url_prefix='/delay')
    app.register_blueprint(flight_bp, url_prefix='/flight')
    app.register_blueprint(flight_type_bp)
    app.register_blueprint(performance_details_bp)
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(scheduled_flight_bp, url_prefix='/scheduled/flight')
    app.register_blueprint(scheduled_report_bp, url_prefix='/scheduled/report')
    app.register_blueprint(select_date_bp, url_prefix='/select')
    app.register_blueprint(user_bp)

    if app.env == 'development':
        init_app_development(app)

def init_app_development(app):
    """
    For development only!
    """
    from .debug import debug_bp
    app.register_blueprint(debug_bp)
