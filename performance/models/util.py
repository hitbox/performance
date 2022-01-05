from itertools import groupby
from operator import attrgetter

flightsortkey = attrgetter('flight_type', 'flight_number_as_int')
flightgroupkey = attrgetter('flight_type')

def grouped_flights(flights):
    return groupby(sorted(flights, key=flightsortkey), flightgroupkey)
