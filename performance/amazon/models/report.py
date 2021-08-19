from datetime import time
from operator import attrgetter

import sqlalchemy as sa

from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property

from performance.extensions import db
from performance.exceptions import AppError
from performance.models import FlightType
from performance.models.mixin import MetaMixin

from .util import grouped_flights

from performance.forms.fields import PercentField

FLIGHTS_BY_TYPE_SORT = attrgetter('origin_departure_estimated_time')

class ReportError(AppError):
    pass


def by_estimated_departure(flight):
    if isinstance(flight.origin_departure_estimated_time, time):
        return flight.origin_departure_estimated_time
    else:
        return time(0,0)

class Report(MetaMixin, db.Model):
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

    performance_meta_id = db.Column(db.Integer, db.ForeignKey('performance_meta.id'))
    # XXX: was this performance_meta field a mistake? think what we need is
    #      objects linked to these reports by month/year and quarter/year.
    # TODO: need month/year object that stores "assumed best lanes" and possibly other things.
    performance_meta = db.relationship('performance.amazon.models.performance_meta.PerformanceMeta')

    # TODO: all these can be removed with the "automatic calculation" changes?
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

    arrival_performance_mtd_30_percent = db.Column(
        db.Float, info=dict(form_field_class=PercentField))
    arrival_performance_mtd_30_lanes = db.Column(db.Integer)
    arrival_performance_mtd_30_late = db.Column(db.Integer)

    @hybrid_property
    def date_quarter(self):
        """
        The quarter part of the date.
        """
        return (self.date.month - 1) // 3 + 1

    @date_quarter.expression
    def date_quarter(cls):
        """
        The quarter part of the date.
        """
        # quarter of a date calculation
        # (month - 1) // 3 + 1
        # XXX: sa.func.div postgres specific
        quarter = sa.func.div(
            sa.cast(
                sa.func.date_part('month', Report.date) - 1,
                sa.Integer),
            3) + 1
        return quarter

    def grouped_flights(self):
        return grouped_flights(self.flights)

    def flights_by_type(self):
        # [(flight_type, flight of that type), ...]
        grouped = [
            (flight_type,
             sorted(
                 (flight for flight in self.flights if flight.flight_type == flight_type),
                 key = by_estimated_departure))
            for flight_type in FlightType.query.order_by(FlightType.report_order)
        ]
        return grouped

    def lane_flights(self):
        return [flight for flight in self.flights if flight.is_lane]

    def controllable_destination_delays(self, over_minutes):
        """
        All report's flights controllable destination delay codes.
        """
        include_types = FlightType.query.filter(FlightType.name == 'Scheduled').all()
        if not include_types:
            raise ReportError('List of flight types to include is empty')
        return [
            delay
            for flight in self.flights
            for delay in flight.controllable_destination_delays(over_minutes)
            if flight.flight_type in include_types]
