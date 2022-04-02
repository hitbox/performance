import datetime
import unittest

from performance.models import Flight

class TestFlight(unittest.TestCase):

    @unittest.skip('trash')
    def test_flight_validate_delays(self):
        # TODO
        flight = Flight(
            origin_departure_estimated_time = datetime.time(0,0),
            origin_departure_actual_time = datetime.time(0,5),
        )
        raise ValueError


if __name__ == '__main__':
    unittest.main()
