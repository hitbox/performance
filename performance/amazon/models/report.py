from collections import defaultdict
from itertools import groupby
from operator import attrgetter

from ...extensions import db
from ...models.flight_type import FlightType
from ...models.mixin import MetaMixin
from ...sorting import flight_sort_key

flightsortkey = attrgetter('flight_type', 'flight_number_as_int')
flightgroupkey = attrgetter('flight_type')

class Report(
    MetaMixin,
    db.Model,
):
    """
    Amazon Performance Report.
    """

    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.Date)
    flights = db.relationship('performance.amazon.models.flight.Flight',
                              backref='report', cascade='all,delete-orphan')
    system_detail = db.Column(
        db.Text,
        info = dict(
            label = 'System Detail',
        ),
    )

    # NOTE: previous is actual today (legacy problem).
    previous_days_performance_percent = db.Column(db.Float)
    previous_days_performance_lanes = db.Column(db.Integer)
    previous_days_performance_late = db.Column(db.Integer)

    arrival_performance_mtd_percent = db.Column(db.Float)
    arrival_performance_mtd_lanes = db.Column(db.Integer)
    arrival_performance_mtd_late = db.Column(db.Integer)

    days_at_100_percent = db.Column(db.Integer)

    qtd_performance_percent = db.Column(db.Float)
    qtd_performance_lanes = db.Column(db.Integer)
    qtd_performance_late = db.Column(db.Integer)

    assumed_best_arrival_performance_for_month_percent = db.Column(db.Float)
    assumed_best_arrival_performance_for_month_lanes = db.Column(db.Integer)
    assumed_best_arrival_performance_for_month_late = db.Column(db.Integer)

    arrival_performance_mtd_30_percent = db.Column(db.Float)
    arrival_performance_mtd_30_lanes = db.Column(db.Integer)
    arrival_performance_mtd_30_late = db.Column(db.Integer)

    def grouped_flights(self):
        return groupby(sorted(self.flights, key=flightsortkey), flightgroupkey)



class ScheduledReport(
    MetaMixin,
    db.Model,
):
    """
    Scheduled reports hold minimal flights to populate new reports on the
    effective datetime start.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    scheduled_flights = db.relationship('ScheduledFlight', backref='scheduled_report')
