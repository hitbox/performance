from flask import current_app

from operator import attrgetter
from operator import itemgetter

from performance.models import FlightType

from performance.dhl.models import Bound
from performance.dhl.models import Flight

def convert_excel_schedule_flights(preview):
    """
    Return the simple data in `preview` as Flight models.
    """
    hub_name = current_app.config['PERFORMANCE_HUB_STATION_NAME']
    flight_type = current_app.config['PERFORMANCE_SCHEDULED_FLIGHT_TYPE_NAME']
    inbound_name = current_app.config['PERFORMANCE_INBOUND_NAME']
    outbound_name = current_app.config['PERFORMANCE_OUTBOUND_NAME']

    flight_type = FlightType.query.filter(FlightType.name == flight_type).one()
    inbound = Bound.query.filter(Bound.name == inbound_name).one()
    outbound = Bound.query.filter(Bound.name == outbound_name).one()

    flights = [
        Flight(
            flight_number = data['flight'],
            bound = inbound if data['dest'] == hub_name else outbound,
            flight_type = flight_type,
            origin_station = data['org'],
            destination_station = data['dest'],
            origin_departure_estimated_time = data['utc_dep'],
            destination_arrival_estimated_time = data['utc_arr'],
        )
        for data in preview
    ]
    return flights

def grouped_flights(report):
    """
    Return a list of flights grouped by ALL `flight_type` and `bound` objects.

    [((flight_type, bound), flights), ...]
    """
    grouped = [
        ((flight_type, bound),
         sorted(
             (flight for flight in report.flights
              if flight.flight_type == flight_type and flight.bound == bound),
             key = attrgetter('flight_number')))
        for flight_type in FlightType.query.order_by(FlightType.report_order)
        for bound in Bound.query.order_by(Bound.report_order)
    ]
    return grouped

def sort_scheduled_flights_from_excel(data):
    _sortkey = itemgetter('flight', 'utc_dep')
    def sortkey(row):
        flight, utc_dep = _sortkey(row)
        try:
            flight = int(flight)
        except ValueError:
            pass
        return flight, utc_dep

    data = sorted(data, key=sortkey)
    return data
