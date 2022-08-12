import datetime

import pytest
import sqlalchemy as sa

from performance import business
from performance import parse
from performance.extensions import db
from performance.models import Delay
from performance.models import DestinationDelay
from performance.models import Flight
from performance.models import FlightType
from performance.models import OriginDelay
from performance.models import Report

def test_more_than_one_chargeable(app):
    with app.app_context():
        # add
        flight_types = \
        test_flight_type1, \
        test_flight_type_chargeable = [
            FlightType(
                name = 'Test1',
                is_controllable = False
            ),
            FlightType(
                name = 'TestChargeableFlightType',
                is_controllable = True,
            ),
        ]
        db.session.add_all(flight_types)
        # mix in some chargeable delays
        delay_objects = [
            Delay(code='abc', is_controllable=True),
            Delay(code='def', is_controllable=False),
            Delay(code='ghi', is_controllable=True),
        ]
        db.session.add_all(delay_objects)
        db.session.commit()
        #
        flight = Flight(
            report = Report(
                date = datetime.date(1970,1,1),
            ),
            # chargeable flight type
            flight_type = test_flight_type_chargeable,
            origin_delays_string = 'ABC1 ABC GHI3',
            # two chargeable destination delay over 15 and 30
            destination_delays_string = 'ABC1 ABC GHI99 ABC99',
        )
        db.session.add(flight)
        db.session.commit()
        #
        data = business.performance_summary(datetime.date(1970,1,1))
        assert len(data) == 3
        assert data['daily']['flights_with_controllable_destination_delays_over15'] == 2
        assert data['daily']['flights_with_controllable_destination_delays_over30'] == 2
