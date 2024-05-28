from collections import defaultdict

import sqlalchemy as sa

from . import models
from . import queries
from . import settings
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

coerce_flight_number = models.Flight.flight_number.type.python_type

def default_flight_type():
    """
    Return a default FlightType object or raise if not found.
    """
    stmt = (
        db.select(models.FlightType)
        .where(models.FlightType.name == 'Scheduled')
    )
    return db.session.scalars(stmt).one()

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

def external_stmt(report_date):
    """
    Query statement to get baggage weight from external source matching
    departure date against report date.
    """
    stmt = (
        db.select(
            sa.cast(models.Leg.fn_number, sa.String(4)).label('fn_number'),
            # datetimes broken apart into date and time, on the python side
            models.Leg.dep_dt,
            models.Leg.arr_dt,
            models.LegPax.baggage_weight_integer.label('baggage_weight_kg'),
            models.LegPax.baggage_weight_lbs_integer.label('baggage_weight_lbs'),
        )
        .outerjoin(
            models.LegPax,
            models.Leg.leg_no == models.LegPax.leg_no,
        )
        .where(
            models.Leg.fn_carrier == settings.external_fn_carrier(),
            models.LegPax.usage == settings.external_usage(),
            sa.func.trunc(models.Leg.dep_dt) == report_date,
        )
        .order_by(
            models.Leg.dep_dt,
            models.Leg.fn_number,
        )
    )
    return stmt

def external_results(report_date):
    """
    Get flight data for a date from an external database.
    """
    stmt = external_stmt(report_date)
    return db.session.execute(stmt)

def date_is_changed(report, olddate, newdate):
    # special consideration for the fallback to report date for flights
    return (
        olddate is not None
        and olddate != report.date
        and olddate != newdate
    )

def get_changes_for_report_from_external(report, results):
    """
    Given the results from an external database, return list of changes to make
    to the flights of a report.
    """
    results = list(results)
    for flight in report.flights:
        for row in results:
            if flight.flight_number != coerce_flight_number(row.fn_number):
                continue
            # flight numbers match for report date
            dep_dt_date = row.dep_dt.date()
            dep_dt_time = row.dep_dt.time()
            arr_dt_date = row.arr_dt.date()
            arr_dt_time = row.arr_dt.time()

            data = dict(
                # existing flight data
                flight = flight,

                # data from external follows
                dep_dt_date = dep_dt_date,
                dep_dt_time = dep_dt_time,
                dep_dt_date_is_diff = date_is_changed(
                    report,
                    flight.origin_departure_actual_date,
                    dep_dt_date,
                ),
                dep_dt_time_is_diff = dep_dt_time != flight.origin_departure_actual_time,

                arr_dt_date = arr_dt_date,
                arr_dt_time = arr_dt_time,
                arr_dt_date_is_diff = date_is_changed(
                    report,
                    flight.destination_arrival_actual_date,
                    arr_dt_date,
                ),
                arr_dt_time_is_diff = arr_dt_time != flight.destination_arrival_actual_time,

                baggage_weight_kg = row.baggage_weight_kg,
                baggage_weight_lbs = row.baggage_weight_lbs,
                baggage_weight_lbs_is_diff = row.baggage_weight_lbs != flight.weight,
            )
            yield data

def new_report_from_external(report_date, results_data):
    """
    :param report_date: date of new report.
    :param results_data: flight and report data, as from ResultsForm.
    """
    report = models.Report(date=report_date)
    # XXX
    # - FlightType is not enforced as a requirement
    # - if it is not given, the flights will not appear on the report
    flight_type = default_flight_type()
    for row in results_data['rows']:
        flight = models.Flight(
            flight_number = row['fn_number'],
            flight_type = flight_type,
        )

        if not row['dep_dt']:
            dep_time = None
        else:
            dep_time = row['dep_dt'].time()
        flight.origin_departure_actual_time = dep_time

        if not row['arr_dt']:
            arr_time = None
        else:
            arr_time = row['arr_dt'].time()
        flight.destination_arrival_actual_time = arr_time

        flight.weight = row['baggage_weight_lbs']

        report.flights.append(flight)
    return report

def update_report_from_external_results(results_data):
    """
    :param results_data:
        flight and report data, as from the FlightChangesForm forms.
    """
    breakpoint()
    for flight_change in results_data['flight_changes']:
        pass
