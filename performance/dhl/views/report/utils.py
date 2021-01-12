from operator import attrgetter
from operator import itemgetter

from performance.models import FlightType

from performance.dhl.models import Bound

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
