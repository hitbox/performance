import datetime as dt
import unittest

from performance.extensions import db
from performance.models import Delay
from performance.models import DelayCode
from performance.models import Flight
from performance.models import FlightType
from performance.models import Leg
from performance.models import Report
from performance.models import Station
from performance.models import User

from tests.base import BaseTest

class TestModels(BaseTest):

    def check_add_and_query(self, modelclass, kwargs, criteria):
        with self.app.app_context():
            inst = modelclass(**kwargs)
            db.session.add(inst)
            db.session.commit()
            if not isinstance(criteria, (tuple, list)):
                criteria = (criteria, )
            modelclass.query.filter(*criteria).one()
            return inst

    def test_delay(self):
        with self.app.app_context():
            leg = Leg(id=1)
            db.session.add(leg)
            db.session.commit()
        kwargs = dict(flightleg_id=1, position=1)
        criteria = (Delay.flightleg_id == 1, Delay.position == 1)
        delay = self.check_add_and_query(Delay, kwargs, criteria)

    def test_delaycode(self):
        kwargs = dict(name='abc')
        criteria = DelayCode.name == 'ABC'
        self.check_add_and_query(DelayCode, kwargs, criteria)

    def test_flight(self):
        kwargs = dict(id=1)
        criteria = Flight.id == 1
        self.check_add_and_query(Flight, kwargs, criteria)

    def test_flighttype(self):
        kwargs = dict(name = 'Case sensitive')
        criteria = FlightType.name == 'Case sensitive'
        self.check_add_and_query(FlightType, kwargs, criteria)

    def test_leg(self):
        kwargs = dict(id=1)
        criteria = Leg.id == 1
        self.check_add_and_query(Leg, kwargs, criteria)

    def test_report(self):
        kwargs = dict(date=dt.date(1970,1,1))
        criteria = Report.date == dt.date(1970,1,1)
        self.check_add_and_query(Report, kwargs, criteria)

    def test_station(self):
        kwargs = dict(code='abc')
        criteria = Station.code == 'ABC'
        self.check_add_and_query(Station, kwargs, criteria)

    def test_user(self):
        kwargs = dict(username = 'test')
        criteria = User.username == 'test'
        self.check_add_and_query(User, kwargs, criteria)


if __name__ == '__main__':
    unittest.main()
