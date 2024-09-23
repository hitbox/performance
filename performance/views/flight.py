from datetime import datetime

from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import request
from flask import url_for

from performance import parse
from performance import queries
from performance.authorization import edit_check
from performance.extensions import db
from performance.models import Flight
from performance.models import FlightType
from performance.models import Report
from performance.pluggable import CreateView
from performance.pluggable import UpdateView
from performance.utils import diff_minutes as diff_minutes_func
from performance.utils import massage_time

flight_bp = Blueprint('flight', __name__)

@edit_check
@flight_bp.before_request
def before_request():
    """
    Enforce edit access.
    """

def flight_form_class():
    # NOTE: temp workaround for wtforms-alchemy's aggressiveness
    from ..forms import FlightForm
    return FlightForm

@flight_bp.context_processor
def context_processor():
    """
    Javascript injection for calculating estimated/actual diff minutes.
    """
    # NOTE: more injection is done inside the templates
    context = dict(
        javascript_injection = dict(
            FLIGHT_CALCS = url_for('.flight_calculations'),
        ),
    )
    return context

@flight_bp.route('/calcs', methods=['POST'])
def flight_calculations():
    """
    API point to return the estimated/actual difference in minutes and delay
    codes string processing for a flight.
    """
    # need flight id to use report for date fallback
    data = request.get_json()

    # defaults
    result = dict(
        minutes = None,
        delays_string = data['delayCodes'],
    )

    # update with minutes--delays uses it
    try:
        result['minutes'] = _diff_minutes(data)
    except (TypeError, ValueError):
        pass

    data['minutes'] = result['minutes']
    result['delays_string'] = _delays(data)

    return jsonify(result)

def _diff_minutes(data):
    """
    Calculate estimated/actual difference in minutes.
    """
    fallback_date = datetime.fromisoformat(data['fallbackDate'])

    est_date = data['estimatedDate']
    est_time = massage_time(data['estimatedTime'])
    act_date = data['actualDate']
    act_time = massage_time(data['actualTime'])

    if not est_date:
        est_date = fallback_date
    else:
        est_date = datetime.fromisoformat(est_date).date()

    if not act_date:
        act_date = fallback_date
    else:
        act_date = datetime.fromisoformat(act_date).date()

    est_time = datetime.strptime(est_time, '%H%M').time()
    act_time = datetime.strptime(act_time, '%H%M').time()

    minutes = diff_minutes_func(est_date, est_time, act_date, act_time)
    return minutes

def _delays(data):
    """
    Delay code processing for frontend. Add place holder delay code for
    unaccounted-for late minutes from data.
    """
    delay_codes = data['delayCodes']
    delay_data = parse.delaystring(delay_codes)

    # placeholder processing
    # ignoring existing placeholders
    delay_data = [delay for delay in delay_data if delay['code'] != parse.PLACEHOLDER_CODE]

    # add placeholder delay code for unaccounted late minutes
    minutes = data['minutes']
    if minutes and minutes > 0:
        accounted_minutes = sum(
            delay['minutes'] for delay in delay_data
            if delay['minutes'] is not None
        )
        missing_minutes = minutes - accounted_minutes
        if missing_minutes > 0:
            placeholder_delay = dict(
                code = parse.PLACEHOLDER_CODE,
                minutes = missing_minutes,
                is_cancelled = False,
            )
            delay_data += [placeholder_delay]

    # back to human readable
    delays_string = parse.formatdelays(delay_data)

    return delays_string

def create_context_processor():
    report_id = request.view_args['report_id']
    report = db.session.get(Report, report_id)
    context = dict(
        fallbackDate = report.date,
        report = report,
    )
    return context

def update_delete_context_processor():
    flight_id = request.view_args['id']
    flight = Flight.query.get(flight_id)
    context = dict(
        fallbackDate = flight.report.date,
        report = flight.report,
    )
    return context

def redirect_for_delete(form):
    return redirect(url_for('report.view_report', id=form.report_id.data))

# create flight
# NOTE: forms will snag report_id out of the request.view_args
flight_bp.add_url_rule(
    '/create/<int:report_id>/<int:flight_type_id>',
    view_func = CreateView.as_view(
        'create',
        flight_form_class,
        model = Flight,
        template = 'flight/form.html',
        context_processor = create_context_processor,
    ))

# update and delete flight
flight_bp.add_url_rule(
    '/edit/<int:id>',
    view_func = UpdateView.as_view(
        'edit',
        flight_form_class,
        model = Flight,
        instance_query = lambda id: Flight.query.get_or_404(id),
        template = 'flight/form.html',
        context_processor = update_delete_context_processor,
        redirect_for_delete = redirect_for_delete,
    ))
