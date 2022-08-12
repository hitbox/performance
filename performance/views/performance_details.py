from flask import Blueprint
from flask import render_template

from .. import business
from ..models import Flight
from ..models import Report

performance_details_bp = Blueprint(
    'performance_details',
    __name__,
    url_prefix = '/performance/details',
)

DATE_RANGE_KEYS = ', '.join(
    business.PERFORMANCE_DATE_RANGE_KEYS
    + ['contract_range']
)

PERFORMANCE_KEYS = ', '.join([
    'lanes',
    'flights_with_controllable_destination_delays_over15',
    'flights_with_controllable_destination_delays_over30',
])

PERFORMANCE_DATE_RANGE_NICE_NAMES = {
    'daily': 'Daily',
    'month_to_date': 'MTD',
    'quarter_to_date': 'QTD',
    'contract_range': 'Contract',
}

PERFORMANCE_KEY_NICE = {
    'lanes': 'Lanes',
    'flights_with_controllable_destination_delays_over15': '>15',
    'flights_with_controllable_destination_delays_over30': '>30',
}

@performance_details_bp.route(
    '/<date:report_date>'
    f'/<any({DATE_RANGE_KEYS}):date_range_key>'
    f'/<any({PERFORMANCE_KEYS}):performance_key>'
)
def for_range(
    report_date,
    date_range_key,
    performance_key,
):
    # Report.date is enforced unique
    report = Report.query.filter(Report.date == report_date).first_or_404()
    contract = business.performance_contract_for_date(report_date)

    nested_queries = business._performance_queries(report_date, contract)

    flight_query = nested_queries[date_range_key][performance_key]
    flight_query = flight_query.order_by(
        Report.date,
        Flight.origin_departure_estimated_time,
    )

    context = dict(
        report = report,
        flights = flight_query.all(),
        date_range_name = PERFORMANCE_DATE_RANGE_NICE_NAMES[date_range_key],
        key_name = PERFORMANCE_KEY_NICE[performance_key],
    )
    return render_template('flight/detail.html', **context)
