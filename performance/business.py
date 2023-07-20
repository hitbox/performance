from . import queries
from .extensions import db

PERFORMANCE_DATE_RANGE_KEYS = [
    'daily',
    'month_to_date',
    'quarter_to_date',
]

PERFORMANCE_CRITERIAS = [
    queries.date_criteria,
    queries.month_to_date_criteria,
    queries.quarter_to_date_criteria,
]

PERFORMANCE_SUMMARY = list(zip(PERFORMANCE_DATE_RANGE_KEYS, PERFORMANCE_CRITERIAS))

def performance_contract_for_date(date):
    """
    Return the performance contract for a (report) date.
    """
    query = queries.performance_contract_query(date)
    return db.session.scalars(query).first()

def _performance_queries(date, contract=None):
    """
    The performance numbers queries inside a nested dictionary.
    """
    long_prefix = 'flights_with_controllable_destination_delays'

    nested_queries = dict()
    for performance_name, criteria_func in PERFORMANCE_SUMMARY:
        criteria = criteria_func(date)
        subdict = nested_queries[performance_name] = dict()
        subdict['lanes'] = queries.lanes(criteria)
        subdict[f'{long_prefix}_over15'] = (
            queries.flights_with_controllable_destination_delays(criteria, 15)
        )
        subdict[f'{long_prefix}_over30'] = (
            queries.flights_with_controllable_destination_delays(criteria, 30)
        )

    if contract:
        criteria = queries.contract_range_criteria(date, contract)
        subdict = nested_queries['contract_range'] = dict()
        subdict['lanes'] = queries.lanes(criteria)
        subdict[f'{long_prefix}_over15'] = (
            queries.flights_with_controllable_destination_delays(criteria, 15)
        )

    return nested_queries

def performance_summary(date, contract=None):
    """
    Return performance numbers (counts) for a report.
    """
    # result the query objects with `.count()`
    queries = _performance_queries(date, contract)
    result = dict()
    for date_range_name, subdict in queries.items():
        result[date_range_name] = dict()
        for performance_name, query in subdict.items():
            result[date_range_name][performance_name] = query.count()
    return result
