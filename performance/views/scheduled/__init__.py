from flask import Blueprint

from .scheduled_flight import scheduled_flight_bp
from .scheduled_report import scheduled_report_bp

scheduled_bp = Blueprint('scheduled', __name__)

scheduled_bp.register_blueprint(scheduled_flight_bp, url_prefix='/flight')
scheduled_bp.register_blueprint(scheduled_report_bp, url_prefix='/report')
