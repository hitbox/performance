from datetime import datetime

from flask import Blueprint
from flask import jsonify
from flask import request
from flask import url_for

from performance import parse
from performance import queries
from performance.authorization import edit_check
from performance.models import Flight
from performance.models import FlightType
from performance.models import Report
from performance.utils import diff_minutes as diff_minutes_func
from performance.utils import massage_time
from performance.views.pluggable import CreateView
from performance.views.pluggable import SimpleListView
from performance.views.pluggable import UpdateDeleteView

flight_bp = Blueprint('flight', __name__)

def flight_form_class():
    # NOTE: temp workaround for wtforms-alchemy's aggressiveness
    from ..forms import FlightForm
    return FlightForm

def create_context_processor():
    # XXX: shares a lot with forms.flight.FlightForm:__init__
    report_id = request.view_args['report_id']
    report = Report.query.get(report_id)
    context = dict(
        fallbackDate = report.date,
        report = report,
    )
    return context

def update_delete_context_processor():
    # XXX: shares a lot with forms.flight.FlightForm:__init__
    flight_id = request.view_args['id']
    flight = Flight.query.get(flight_id)
    context = dict(
        fallbackDate = flight.report.date,
        report = flight.report,
    )
    return context

def detail_query(date_criteria):
    """
    Flights for some criteria of dates.
    """
    return (Flight.query
        .join(Report)
        .join(FlightType)
        .filter(date_criteria)
        .order_by(
            Report.date,
            FlightType.report_order,
            Flight.origin_departure_estimated_time,
        ))

def contract_items():
    contract_id = request.view_args['contract_id']
    contract = Contract.get_or_404(request.view_args['contract_id'])
    criteria = queries.contract_range_criteria(contract)
    return detail_query(criteria).all()

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
@edit_check
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

# create flight
flight_bp.add_url_rule(
    '/create/<int:report_id>',
    view_func = edit_check(
        CreateView.as_view(
            'create',
            flight_form_class,
            template = 'flight/form.html',
            context_processor = create_context_processor,
        )))

# edit flight
flight_bp.add_url_rule(
    '/edit/<int:id>',
    view_func = edit_check(
        UpdateDeleteView.as_view(
            'edit',
            flight_form_class,
            instance_query = lambda id: Flight.query.get_or_404(id),
            template = 'flight/form.html',
            context_processor = update_delete_context_processor,
        )))

# daily flights
flight_bp.add_url_rule(
    '/detail/daily/<date:date>',
    view_func = SimpleListView.as_view(
        'detail_daily',
        template = 'flight/list.html',
        extra_context = lambda: dict(
            hide_date = True,
            title = 'Daily',
        ),
        items_getter = lambda:
            detail_query(
                Report.date == request.view_args['date']
            ).all(),
    ))

# month to date flights
flight_bp.add_url_rule(
    '/detail/mtd/<date:date>',
    view_func = SimpleListView.as_view(
        'detail_mtd',
        template = 'flight/list.html',
        extra_context = lambda: dict(
            title = 'Month to date',
        ),
        items_getter = lambda:
            detail_query(
                queries.month_to_date_criteria(
                    request.view_args['date']
                )
            ).all(),
    ))

# quarter to date flights
flight_bp.add_url_rule(
    '/detail/qtd/<date:date>',
    view_func = SimpleListView.as_view(
        'detail_qtd',
        template = 'flight/list.html',
        extra_context = lambda: dict(
            title = 'Quarter to date',
        ),
        items_getter = lambda:
            detail_query(
                queries.quarter_to_date_criteria(
                    request.view_args['date']
                )
            ).all(),
    ))

# contract date range of flights
flight_bp.add_url_rule(
    '/detail/contract/<int:contract_id>',
    view_func = SimpleListView.as_view(
        'detail_contract',
        template = 'flight/list.html',
        extra_context = lambda: dict(
            title = 'Quarter to date',
        ),
        items_getter = lambda: contract_items(),
    ))

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
    delay_objects = parse.delaystring(delay_codes)

    # placeholder processing
    # ignoring existing placeholders
    delay_objects = [delay for delay in delay_objects if delay['code'] != parse.PLACEHOLDER_CODE]

    # add placeholder delay code for unaccounted late minutes
    minutes = data['minutes']
    if minutes and minutes > 0:
        accounted_minutes = sum(
            delay.minutes for delay in delay_objects
            if delay.minutes is not None
        )
        missing_minutes = minutes - accounted_minutes
        if missing_minutes > 0:
            placeholder_delay = dict(
                code = parse.PLACEHOLDER_CODE,
                minutes = missing_minutes,
                is_cancelled = False,
            )
            delay_objects += [placeholder_delay]

    # back to human readable
    delays_string = parse.formatdelays(delay_objects)

    # uppercasing is normally done by Flight model validation
    # TODO: uppercasing is done by the custom data type
    delays_string = delays_string.upper()
    return delays_string
