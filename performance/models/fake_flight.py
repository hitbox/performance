from datetime import date
from datetime import time

from collections import namedtuple

class FakeFlight(
    namedtuple(
        'FakeFlightBase',
        [
            'tail_number_with_prefix',
            'flight_number',
            'origin_station',
            'destination_station',
            'weight',
            'actual_departure_datetime',
            'actual_arrival_datetime',
        ],
    )
):
    """
    Simple convenience class for the results of the external query results.
    """

    _tail_number_strip_prefix = 'N'

    # Properties to match internal Flight objects.

    @property
    def tail_number(self):
        tail_number = self.tail_number_with_prefix
        if tail_number:
            tail_number = tail_number.removeprefix(self._tail_number_strip_prefix)
            return tail_number

    @property
    def origin_departure_actual_date(self):
        if self.actual_departure_datetime:
            return self.actual_departure_datetime.date()

    @property
    def origin_departure_actual_time(self):
        if self.actual_departure_datetime:
            return self.actual_departure_datetime.time()

    @property
    def destination_arrival_actual_date(self):
        if self.actual_arrival_datetime:
            return self.actual_arrival_datetime.date()

    @property
    def destination_arrival_actual_time(self):
        if self.actual_arrival_datetime:
            return self.actual_arrival_datetime.time()
