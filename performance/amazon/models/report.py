from operator import attrgetter

from flask import current_app

from performance.extensions import db
from performance.models import FlightType
from performance.models.mixin import MetaMixin

from .util import grouped_flights

FLIGHTS_BY_TYPE_SORT = attrgetter('origin_departure_estimated_time')

from performance.forms.fields import PercentField

class Report(
    MetaMixin,
    db.Model,
):
    """
    Amazon Performance Report.
    """

    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.Date)
    flights = db.relationship(
        'performance.amazon.models.flight.Flight',
        backref = 'report',
        cascade = 'all,delete-orphan',
    )
    system_detail = db.Column(
        db.Text,
        info = dict(
            label = 'System Detail',
        ),
    )

    # NOTE: previous is actually today (legacy problem).
    previous_days_performance_percent = db.Column(
        db.Float, info=dict(form_field_class=PercentField))
    previous_days_performance_lanes = db.Column(db.Integer)
    previous_days_performance_late = db.Column(db.Integer)

    arrival_performance_mtd_percent = db.Column(
        db.Float, info=dict(form_field_class=PercentField))
    arrival_performance_mtd_lanes = db.Column(db.Integer)
    arrival_performance_mtd_late = db.Column(db.Integer)

    days_at_100_percent = db.Column(db.Integer)

    qtd_performance_percent = db.Column(
        db.Float, info=dict(form_field_class=PercentField))
    qtd_performance_lanes = db.Column(db.Integer)
    qtd_performance_late = db.Column(db.Integer)

    assumed_best_arrival_performance_for_month_percent = db.Column(
        db.Float, info=dict(form_field_class=PercentField))
    assumed_best_arrival_performance_for_month_lanes = db.Column(db.Integer)
    assumed_best_arrival_performance_for_month_late = db.Column(db.Integer)

    assumed_best_lanes = db.Column(db.Integer)

    arrival_performance_mtd_30_percent = db.Column(
        db.Float, info=dict(form_field_class=PercentField))
    arrival_performance_mtd_30_lanes = db.Column(db.Integer)
    arrival_performance_mtd_30_late = db.Column(db.Integer)

    def grouped_flights(self):
        return grouped_flights(self.flights)

    def flights_by_type(self):
        # [(flight_type, flight of that type), ...]
        grouped = [
            (flight_type,
             sorted(
                 (flight for flight in self.flights if flight.flight_type == flight_type),
                 key = FLIGHTS_BY_TYPE_SORT))
            for flight_type in FlightType.query.order_by(FlightType.report_order)
        ]
        return grouped

    def lanes(self):
        return len(self.flights)

    def chargeable_delays(self):
        controllable = current_app.config['PERFORMANCE_CONTROLLABLE']
        return [
            (delay_code, minutes)
            for flight in self.flights
            for delay_code, minutes in flight.destination_delay_codes()
            if delay_code in controllable
        ]

    def over30(self):
        controllable = current_app.config['PERFORMANCE_CONTROLLABLE']
        extra_controllable = current_app.config['PERFORMANCE_EXTRA_INFO_CONTROLLABLE']
        all_controllable = controllable + extra_controllable
        delay_codes = [
            (delay_code, minutes)
            for flight in self.flights
            for delay_code, minutes in flight.origin_delay_codes()
            if delay_code in all_controllable
            and minutes is not None
            and minutes > 30
        ]
        return delay_codes
