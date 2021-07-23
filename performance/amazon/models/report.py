from datetime import time
from operator import attrgetter

from flask import current_app

from performance.extensions import db
from performance.models import FlightType
from performance.models.mixin import MetaMixin

from .util import grouped_flights

from performance.forms.fields import PercentField

FLIGHTS_BY_TYPE_SORT = attrgetter('origin_departure_estimated_time')

def by_estimated_departure(flight):
    if isinstance(flight.origin_departure_estimated_time, time):
        return flight.origin_departure_estimated_time
    else:
        return time(0,0)

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

    def lanes(self):
        # TODO
        # * should only be included in the count if they are a
        #   "scheduled flight", or an "extra-CMI AMZ Flight".
        # * Do not include "extra non-cmi amz flights" in the LANE count. These
        #   apply for DAILY, MONTHLY and QTD.
        # * One exception: if Origin and Dest are the same, it will NOT count
        #   in the LANE count (this would be like ILN-ILN for a ground
        #   turnback/example).
        # * Right now, it is including the "non-cmi" flights in the counts. On
        #   the 13Jul21 report, I manually filled in the performance numbers
        #   for a comparison to the first calculation section.
        return len(self.flights)

    def chargeable_delays(self):
        # TODO:
        # should only be counted as Chargeable if the Delay Codes (2nd delay
        # code column) in the Arrival are equal to:
        #
        # MXA with minutes greater than >15 and >30 respectively
        # DSP with minutes greater than >15 and >30 respectively
        # CRW with minutes greater than >15 and >30 respectively
        #
        # XLD MXA  (no minutes will be listed if XLD) Will count in both the >15 column and >30 column
        # XLD CRW (no minutes will be listed if XLD) Will count in both the >15 column and >30 column
        # XLD DSP (no minutes will be listed if XLD) Will count in both the >15 column and >30 column
        controllable = current_app.config['PERFORMANCE_CONTROLLABLE']
        return [
            (delay_code, minutes)
            for flight in self.flights
            for delay_code, minutes in flight.destination_delay_codes()
            if delay_code in controllable
        ]

    def over30(self):
        # TODO: see chargeable_delays above
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
