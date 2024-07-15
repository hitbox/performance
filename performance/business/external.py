import datetime

from operator import attrgetter
from types import SimpleNamespace

from performance import models
from performance import queries
from performance.extensions import db

from performance.utils import popitem

get_external_key = attrgetter(
    'fn_number_as_string',
    'dep_ap_actual',
    'arr_ap_actual',
)

get_internal_key = attrgetter(
    'flight_number',
    'origin_station',
    'destination_station',
)

_flight_sort_key_for_changes = attrgetter(
    'origin_departure_estimated_date',
    'origin_station',
    'destination_station',
)

external_diff_attrs = [
    'dep_dt_date',
    'dep_dt_time',
    'arr_dt_date',
    'arr_dt_time',
    'baggage_weight_lbs',
]

internal_diff_attrs = [
    'origin_departure_actual_date',
    'origin_departure_actual_time',
    'destination_arrival_actual_date',
    'destination_arrival_actual_time',
    'weight',
]

date_and_time_to_delays = {
    'origin_departure_actual_date': 'origin_delays',
    'origin_departure_actual_time': 'origin_delays',
    'destination_arrival_actual_date': 'destination_delays',
    'destination_arrival_actual_time': 'destination_delays',
}

def external_label(attrname):
    for class_ in [models.Leg, models.LegPax]:
        attr = getattr(class_, attrname, None)
        if attr:
            return attr.info['label']

def external_index(row):
    # enumerate-like for the external key
    return (get_external_key(row), row)

def internal_index(flight):
    # enumerate-like for the internal key
    return (get_internal_key(flight), flight)

def post_process_external_flights(external_flights):
    for flight in external_flights:
        flight = SimpleNamespace(**flight._mapping)
        flight.dep_dt_date = datetime.date.fromisoformat(flight.dep_dt_date_string)
        flight.dep_dt_time = datetime.time.fromisoformat(flight.dep_dt_time_string)
        flight.arr_dt_date = datetime.date.fromisoformat(flight.arr_dt_date_string)
        flight.arr_dt_time = datetime.time.fromisoformat(flight.arr_dt_time_string)
        del flight.dep_dt_date_string
        del flight.dep_dt_time_string
        del flight.arr_dt_date_string
        del flight.arr_dt_time_string
        yield flight

def joined_external_flights(report_date):
    """
    Join flight from external database with internal flights for a given report
    date.
    """
    # because these flights come from different sources we join in memory
    external_flights_stmt = queries.get_external_stmt(report_date)
    internal_flights_stmt = queries.get_internal_stmt(report_date)

    external_flights = db.session.execute(external_flights_stmt)
    external_flights = post_process_external_flights(external_flights)

    internal_flights = db.session.scalars(internal_flights_stmt)

    indexed_external_flights = dict(map(external_index, external_flights))
    indexed_internal_flights = dict(map(internal_index, internal_flights))

    joined = []
    while indexed_external_flights and indexed_internal_flights:
        external_key, external_flight = popitem(indexed_external_flights)
        for internal_key, internal_flight in indexed_internal_flights.items():
            if external_key == internal_key:
                joined.append((external_flight, internal_flight))
                break
        else:
            # next while loop, ignore unmatched
            continue
        # internal was found: remove internal flight from consideration
        del indexed_internal_flights[internal_key]

    # TODO
    # - do something with unmatched?
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

def simple_diff(report_date, old, new):
    return old and (old != new)

def date_is_changed(report_date, olddate, newdate):
    # special consideration for the fallback to report date for flights
    if olddate is None:
        # check against fallback to report date
        is_changed = newdate != report_date
    else:
        is_changed = newdate != olddate
    return is_changed

def flight_diff(report_date, external_flight, internal_flight):
    """
    Return list of differences between internal and external flights.
    """
    diffs = []
    attr_items = zip(external_diff_attrs, internal_diff_attrs)
    for external_attr, internal_attr in attr_items:
        diff_func = diff_funcs[external_attr]
        old = getattr(internal_flight, internal_attr)
        new = getattr(external_flight, external_attr)
        is_diff = diff_func(report_date, old, new)
        if is_diff:
            internal_label = getattr(models.Flight, internal_attr).info['label']
            diff = dict(
                internal_attr = internal_attr,
                internal_attr_order = internal_diff_attrs.index(internal_attr),
                internal_label = internal_label,
                external_attr = external_attr,
            )
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
    # TODO
    # - better function name
    changes = []
    for external_flight, internal_flight in joined:
        diffs = flight_diff(
            report_date,
            external_flight,
            internal_flight,
        )
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

def update_from_flight_changes(flight_changes_list):
    """
    Update flights' attributes from a list of differences.
    """
    for flight_changes in flight_changes_list:
        internal_flight_data = flight_changes['internal_flight']
        internal_flight = db.session.get(models.Flight, internal_flight_data['id'])
        external_flight = flight_changes['external_flight']
        for diff in flight_changes['diffs']:
            if not diff['do_update']:
                # user selected not to update this diff
                continue
            internal_attr = diff['internal_attr']
            external_attr = diff['external_attr']
            value = external_flight[external_attr]
            setattr(internal_flight, internal_attr, value)
            if internal_attr not in date_and_time_to_delays:
                # was not a diff affecting the delay codes' minutes
                continue
            delays_attr = date_and_time_to_delays[internal_attr]
            delays = getattr(internal_flight, delays_attr)
            for delay in delays:
                delay.minutes = None

diff_funcs = {
    'dep_dt_date': date_is_changed,
    'dep_dt_time': simple_diff,
    'arr_dt_date': date_is_changed,
    'arr_dt_time': simple_diff,
    'baggage_weight_lbs': simple_diff,
}
