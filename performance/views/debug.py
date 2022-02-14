from flask import Blueprint
from flask import abort
from flask import flash
from flask import render_template

from ..extensions import db
from ..models import Flight
from ..models import Report

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug')
def index():
    """
    Hidden route for developing the flash messages.
    """
    flash('Info Message', 'info')
    flash('Success Message', 'success')
    flash('Warning Message', 'warning')
    flash('Error Message', 'error')
    flash('Multiline flash message\nLine 1\nLine 2', 'info')
    flash('TODO message only for development', 'todo')
    return render_template('debug/debug.html')

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
