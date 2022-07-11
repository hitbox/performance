from flask import Blueprint
from flask import abort
from flask import flash
from flask import render_template
from werkzeug.datastructures import MultiDict
from wtforms import BooleanField
from wtforms import Form
from wtforms import FormField
from wtforms import IntegerField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import validators

from performance.extensions import db
from performance.models import Flight
from performance.models import Report

from .form import debugform_bp

debug_bp = Blueprint('debug', __name__, url_prefix='/debug')

debug_bp.register_blueprint(debugform_bp)

@debug_bp.before_request
def before_request():
    flash('Info Message', 'info')
    flash('Success Message', 'success')
    flash('Warning Message', 'warning')
    flash('Error Message', 'error')
    flash('Multiline flash message\nLine 1\nLine 2', 'info')

@debug_bp.route('/')
def index():
    """
    Hidden route for developing the flash messages.
    """
    return render_template('debug/index.html')

@debug_bp.route('/return-abort/<int:error>')
def return_abort(error):
    abort(error)

@debug_bp.route('/config-delay-codes')
def config_delay_codes():
    """
    Show flights with delay codes that have interesting attributes for this feature.
    """
    interesting_flights = Flight.query.filter(
        db.or_(
            db.and_(
                Flight.origin_delays != None,
                Flight.origin_delays != '',
            ),
            db.and_(
                Flight.destination_delays != None,
                Flight.destination_delays != '',
            ),
        )
    ).join(
        Report,
    ).order_by(
        Report.date,
    ).paginate()
    context = dict(
        interesting_flights = interesting_flights,
    )
    template = 'debug/interesting_flights.html'
    return render_template(template, **context)
