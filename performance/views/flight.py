from datetime import datetime

from flask import Blueprint
from flask import jsonify
from flask import request
from flask import url_for

from performance.authorization import edit_check
from performance.views.pluggable import CreateView
from performance.views.pluggable import UpdateDeleteView

from ..models import Flight
from ..models.flight import diff_minutes as diff_minutes_func

flight_bp = Blueprint('flight', __name__)

def flight_form_class():
    # NOTE: temp workaround for wtforms-alchemy's aggressiveness
    from ..forms import FlightForm
    return FlightForm


flight_bp.add_url_rule(
    '/create/<int:report_id>',
    view_func = edit_check(
        CreateView.as_view(
            'create',
            flight_form_class,
            template = 'flight/form.html',
        )))

flight_bp.add_url_rule(
    '/edit/<int:id>',
    view_func = edit_check(
        UpdateDeleteView.as_view(
            'edit',
            flight_form_class,
            template = 'flight/form.html',
        )))

@flight_bp.context_processor
def context_processor():
    """
    Javascript injection for calculating estimated/actual diff minutes.
    """
    context = dict(
        javascript_injection = dict(
            DIFF_MINUTES_URL = url_for('.diff_minutes'),
        ),
    )
    return context

def massage_time(string):
    # keep only digits
    value = int(''.join(c for c in string if c.isdigit()))
    # left-pad with zero to four places
    value = f'{value:04d}'
    return value

def _diff_minutes(data):
    """
    Calculate estimated/actual difference in minutes.
    """
    flight_id = int(data['flightId'])
    flight = Flight.query.get_or_404(flight_id)

    est_date = data['estimatedDate']
    est_time = massage_time(data['estimatedTime'])
    act_date = data['actualDate']
    act_time = massage_time(data['actualTime'])

    if not est_date:
        est_date = flight.report.date
    else:
        est_date = datetime.fromisoformat(est_date).date()

    if not act_date:
        act_date = flight.report.date
    else:
        act_date = datetime.fromisoformat(act_date).date()

    est_time = datetime.strptime(est_time, '%H%M').time()
    act_time = datetime.strptime(act_time, '%H%M').time()

    minutes = diff_minutes_func(est_date, est_time, act_date, act_time)
    return minutes

@flight_bp.route('/diff/minutes', methods=['POST'])
@edit_check
def diff_minutes():
    """
    Frontend API point for return the estimated/actual difference in minutes
    for a flight.
    """
    # need flight id to use report for date fallback
    data = request.get_json()
    result = dict(minutes=None)
    try:
        result['minutes'] = _diff_minutes(data)
    except (TypeError, ValueError) as e:
        result['status'] = 'error'
    else:
        result['status'] = 'success'
    return jsonify(result)
