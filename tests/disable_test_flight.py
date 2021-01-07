import datetime as dt
import unittest

from performance import parse
from performance.app import create_app
from performance.extensions import db
from performance.models import Delay
from performance.models import DelayCode
from performance.models import Flight
from performance.models import FlightType
from performance.models import Leg
from performance.models import Report

from tests.base import BaseTest

def delays_from_string(s):
    delaylist = parse.delaystring(s)
    delays = [Delay.load_or_new(code, minutes)
              for code, minutes in delaylist]
    return delays

class TestReport(BaseTest):

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            db.session.add(FlightType(name='scheduled'))
            for name in ['AFL', 'MXA', 'RRT']:
                db.session.add(DelayCode(name=name))
            db.session.commit()

    def test_api_flight_get(self):
        with self.app.app_context():
            report = Report(
                date = dt.date(1970, 1, 1),
                system_detail = 'some notes about system detail',
                previous_days_performance_percent = .99,
                previous_days_performance_lanes = 100,
                previous_days_performance_late = 0,
                arrival_performance_mtd_percent = .95,
                arrival_performance_mtd_lanes = 200,
                arrival_performance_mtd_late = 5,
                days_at_100_percent = 1000,
                qtd_performance_percent = .90,
                qtd_performance_lanes = 1500,
                qtd_performance_late = 10,
                assumed_best_arrival_performance_for_month_percent = .85,
                assumed_best_arrival_performance_for_month_lanes = 1750,
                assumed_best_arrival_performance_for_month_late = 20,
                arrival_performance_mtd_30_percent = .83,
                arrival_performance_mtd_30_lanes = 1900,
                arrival_performance_mtd_30_late = 25
            )
            db.session.add(report)
            db.session.commit()


if __name__ == '__main__':
    unittest.main()
