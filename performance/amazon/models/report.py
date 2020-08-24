from collections import defaultdict

from ...extensions import db
from ...models.flight_type import FlightType
from ...models.mixin import MetaMixin
from ...sorting import flight_sort_key

class Report(MetaMixin, db.Model):
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

    def flights_indexed_by_type(self):
        indexed = defaultdict(list)
        for flight in self.flights:
            indexed[flight.flight_type].append(flight)
        return indexed

    def flights_by_type(self):
        indexed = self.flights_indexed_by_type()
        result = [
            # two-tuple (flight type, sorted list of flights)
            (
                flight_type,
                sorted(indexed.get(flight_type, []), key=flight_sort_key),
            )
            # per sorted list of all flight types
            for flight_type in FlightType.query.order_by(FlightType.order)
        ]
        return result


class ScheduledReport(
    db.Model,
    MetaMixin,
):
    """
    Scheduled reports hold minimal flights to populate new reports on the
    effective datetime start.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    scheduled_flights = db.relationship('ScheduledFlight', backref='scheduled_report')

    def flights_indexed_by_type(self):
        indexed = defaultdict(list)
        for flight in self.scheduled_flights:
            indexed[flight.flight_type].append(flight)
        return indexed

    def flights_by_type(self):
        indexed = self.flights_indexed_by_type()
        result = [
            # two-tuple (flight type, sorted list of flights)
            (
                flight_type,
                sorted(indexed.get(flight_type, []), key=flight_sort_key),
            )
            # per sorted list of all flight types
            for flight_type in FlightType.query.order_by(FlightType.order)
        ]
        return result
