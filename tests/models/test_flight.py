import datetime
import unittest

from performance.models import Flight
from performance.models import Report

class TestFlight(unittest.TestCase):
    """
    Testing the flight model.
    """
    attrmap = {
        'origin': [
            'origin_departure_estimated_date',
            'origin_departure_estimated_time',
            'origin_departure_actual_date',
            'origin_departure_actual_time',
        ],
        'destination': [
            'destination_arrival_estimated_date',
            'destination_arrival_estimated_time',
            'destination_arrival_actual_date',
            'destination_arrival_actual_time',
        ],
    }

    def setUp(self):
        self.report = Report(
            date = datetime.date(2000, 1, 1),
        )

    def create_flight(self, est, act, origdest, est_date=None, act_date=None):
        if origdest not in ('origin', 'destination'):
            raise ValueError('Invalid origdest value.')

        attrnames = self.attrmap[origdest]
        kwargs = dict(zip(attrnames, [est_date, est, act_date, act]))
        flight = Flight(report=self.report, **kwargs)
        return flight

    def check_diff(self, est, act, expected, est_date=None, act_date=None):
        """
        Assert time diff minutes for origin and destination.
        """
        # origin
        flight = self.create_flight(est, act, 'origin', est_date, act_date)
        self.assertEqual(flight.origin_diff_minutes_value(), expected)
        # destination
        flight = self.create_flight(est, act, 'destination', est_date, act_date)
        self.assertEqual(flight.destination_diff_minutes_value(), expected)

    def test_flight_diff_minutes(self):
        """
        """
        # 0100 -> None = 0m
        self.check_diff(datetime.time(1,0), None, 0)
        # None -> 0100 = 0m
        self.check_diff(None, datetime.time(1,0), 0)
        # 0000 -> 0100 = 60m
        self.check_diff(datetime.time(0,0), datetime.time(1,0), 60)
        # Jan. 1, 0000 -> Jan. 2, 0000
        self.check_diff(
            datetime.time(0,0),
            datetime.time(0,0),
            60*24, # expected
            act_date = datetime.date(2000,1,2),
        )
        # NOTE: just asserting for what this will do in a time traveling
        #       backwards situation.
        # Jan. 1, 0000 -> Dec. 31 1999, 0000
        self.check_diff(
            datetime.time(0,0),
            datetime.time(0,0),
            -60*24, # expected
            act_date = datetime.date(1999,12,31),
        )


if __name__ == '__main__':
    unittest.main()
