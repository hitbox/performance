from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from werkzeug.exceptions import HTTPException

from ..models import Report
from ..month import Weekday

from . import select_date
from .assumed_best import assumed_best_bp
from .flight import flight_bp
from .report import report_bp
from .scheduled_flight import scheduled_flight_bp
from .scheduled_report import scheduled_report_bp
from .user import user_bp

def init_app(app):
    """
    Initialize views.
    """
    @app.context_processor
    def inject():
        return dict(
            weekday = {n:Weekday(n) for n in range(7)},
        )

    @app.errorhandler(HTTPException)
    def error(e):
        """
        HTTP Error Code page to make everything styled consistently.
        """
        return (render_template('error.html', e=e), e.code)

    @app.route('/')
    def index():
        return redirect(url_for('select_date.goto_today'))

    app.register_blueprint(user_bp)
    app.register_blueprint(assumed_best_bp, url_prefix='/best')
    app.register_blueprint(flight_bp, url_prefix='/flight')
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(scheduled_flight_bp, url_prefix='/scheduled-flight')
    app.register_blueprint(scheduled_report_bp, url_prefix='/scheduled-report')
    # TODO: flatten
    blueprint = select_date.select_date_blueprint(Report, 'date')
    app.register_blueprint(blueprint, url_prefix='/select')
    if app.env == 'development':
        init_app_development(app)

def init_app_development(app):
    """
    For development only!
    """
    from .debug import debug_bp
    from .todo import todo_bp

    app.register_blueprint(todo_bp, url_prefix='/todo')
    app.register_blueprint(debug_bp)
