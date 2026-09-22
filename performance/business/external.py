import math

from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from itertools import chain
from itertools import groupby
from operator import attrgetter
from types import SimpleNamespace

from performance import queries
from performance.extensions import db
from performance.models import Flight
from performance.models import Leg
from performance.models import LegPax
from performance.models import Report
from performance.models import FakeFlight
from performance.utils import popitem
from performance.utils import sorted_groupby

flight_key = attrgetter(
    'normalized_flight_number',
    'origin_station',
    'destination_station',
)

# Sorting key for final changes list.
_flight_sort_key_for_changes = attrgetter(
    'origin_departure_estimated_datetime',
    'origin_station',
    'destination_station',
)

# The attributes to compare between internal and external flights
diff_attrs = [
    'tail_number',
    'origin_departure_actual_date',
    'origin_departure_actual_time',
    'destination_arrival_actual_date',
    'destination_arrival_actual_time',
    'weight',
]

def guess_date_needed(report_date, estimated_time, actual_time):
    est_dt = datetime.combine(report_date, estimated_time)
    act_dt = datetime.combine(report_date, actual_time)
    delta = (act_dt - est_dt)
    seconds = delta.total_seconds()
    if abs(seconds) > 60 * 60 * 12:
        return report_date - timedelta(days = math.copysign(1, seconds))

def get_flight_changes(report_date):
    """
    Return a list of sorted differences between internal and external flights.
    """
    joined = joined_external_flights(report_date)
    flight_changes = make_diffs(report_date, joined)
    flight_changes = sorted(flight_changes, key=changes_sort_key)
    return flight_changes

def joined_external_flights(report_date):
    """
    Join flight from external database with internal flights for a given report
    date.
    """
    # Because these flights come from different databases we join in memory.
    internal_flights_stmt = queries.get_internal_stmt(report_date)
    internal_flights = db.session.scalars(internal_flights_stmt)

    external_flights_stmt = queries.get_external_stmt(report_date)
    external_flights = db.session.execute(external_flights_stmt).mappings()
    external_flights = [FakeFlight(**flight_data) for flight_data in external_flights]

    indexed_internal_flights = {
        flight_key(flight): flight for flight in internal_flights
    }

    indexed_external_flights = {
        flight_key(flight): flight for flight in external_flights
    }

    joined = []
    for key, internal_flight in indexed_internal_flights.items():
        if key in indexed_external_flights:
            external_flight = indexed_external_flights[key]
            joined.append((external_flight, internal_flight))

    return joined

def changes_sort_key(diff):
    """
    Key to sort list of flight changes (make_diffs).
    """
    internal_flight = diff['internal_flight']
    return _flight_sort_key_for_changes(internal_flight)

def external_results(report_date):
    """
    Get flight data for a date from an external database.
    """
    stmt = queries.get_external_stmt(report_date)
    return db.session.execute(stmt)

def simple_is_changed(report_date, old, new):
    return old != new

def date_is_changed(report_date, olddate, newdate):
    if olddate is None and newdate is None:
        return False

    # special consideration for the fallback to report date for flights
    if olddate is None:
        # check against fallback to report date
        is_changed = newdate != report_date
    else:
        is_changed = newdate != olddate
    return is_changed

def time_is_changed(report_date, oldtime, newtime):
    if newtime is None:
        return False
    return oldtime is None or newtime is not None and oldtime != newtime

def flight_diff(report_date, external_flight, internal_flight):
    """
    Return list of differences between internal and external flights.
    """
    diffs = []
    # Simple differences between attributes.
    for attr in diff_attrs:
        internal_value = getattr(internal_flight, attr)
        external_value = getattr(external_flight, attr)
        diff_func = diff_funcs[attr]
        is_diff = diff_func(report_date, internal_value, external_value)
        if is_diff:
            internal_label = getattr(Flight, attr).info['label']
            diff = {
                'internal_attr': attr,
                'internal_attr_order': diff_attrs.index(attr),
                'internal_label': internal_label,
                'external_attr': attr,
            }
            diffs.append(diff)
    return diffs

def get_changes_for_report_from_external(report):
    joined = joined_external_flights(report.date)
    changes = []
    for external_flight, internal_flight in joined:
        diff = flight_diff(report, external_flight, internal_flight)
        if diff:
            diff['external_flight'] = external_flight
            diff['internal_flight'] = internal_flight
            changes.append(diff)
    return changes

def make_diffs(report_date, joined):
    """
    Return a list of internal and external flights that have differences for a
    given report date.
    """
    changes = []
    for external_flight, internal_flight in joined:
        diffs = flight_diff(report_date, external_flight, internal_flight)
        if diffs:
            change = dict(
                diffs = diffs,
                external_flight = external_flight,
                internal_flight = internal_flight,
            )
            changes.append(change)
    return changes

def new_report_from_external(report_date, results_data):
    """
    :param report_date: date of new report.
    :param results_data: flight and report data, as from ResultsForm.
    """
    report = Report(date=report_date)
    # XXX
    # - FlightType is not enforced as a requirement
    # - if it is not given, the flights will not appear on the report
    flight_type = default_flight_type()
    for row in results_data['rows']:
        flight = Flight(
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

def update_from_flight_changes(flight_changes_list):
    """
    Update flights' attributes from a list of differences.
    """
    for flight_changes in flight_changes_list:
        internal_flight_data = flight_changes['internal_flight']
        internal_flight = db.session.get(Flight, internal_flight_data['id'])
        external_flight = flight_changes['external_flight']
        for diff in flight_changes['diffs']:
            if not diff['do_update']:
                # user selected not to update this diff
                continue
            internal_attr = diff['internal_attr']
            external_attr = diff['external_attr']
            value = external_flight[external_attr]
            setattr(internal_flight, internal_attr, value)

diff_funcs = {
    'weight': simple_is_changed,
    'origin_departure_actual_date': date_is_changed,
    'origin_departure_actual_time': time_is_changed,
    'destination_arrival_actual_date': date_is_changed,
    'destination_arrival_actual_time': time_is_changed,
    'tail_number': simple_is_changed,
}
