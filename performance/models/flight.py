import datetime as dt
import string

from flask import current_app

from .. import parse
from ..extensions import db

from .mixin import MetaMixin
from .flight_type import FlightTypeRelationshipMixin

def configured_performance_lanes_flighttypes():
    """
    The FlightType's that count for lanes.
    """
    from .flight_type import FlightType
    flight_types_names = current_app.config['PERFORMANCE_LANES_FLIGHTTYPES']
    flight_types = FlightType.query.filter(FlightType.name.in_(flight_types_names)).all()
    return flight_types

class FlightBaseMixin:
    """
    Columns shared by flights and scheduled flights.
    """

    flight_number = db.Column(
        db.String,
        info = dict(
            label = 'Flight',
        ),
    )

    @property
    def flight_number_as_int(self):
        if self.flight_number:
            s = ''.join(c for c in self.flight_number if c in string.digits)
            if s:
                return int(s)

    leg = db.Column(
        db.Integer,
        server_default = db.text('1'),
        info = dict(
            label = 'Leg',
        ),
    )

    tail_number = db.Column(
        db.String,
        info = dict(
            label = 'Tail',
        ),
    )

    weight = db.Column(
        db.Integer,
        info = dict(
            label = 'Weight',
        ),
    )

    comment = db.Column(
        db.Text,
        info = dict(
            label = 'Comment',
            render_kw = dict(
                cols = 80,
                rows = 8,
            ),
        ),
    )

    origin_station = db.Column(
        db.String,
        index = True,
        info = dict(
            label = 'Orig. Station',
        ),
    )
    origin_departure_estimated_date = db.Column(
        db.Date,
        info = dict(
            label = 'ETD',
            render_kw = dict(
                class_ = 'date-entry',
                placeholder = 'optional date',
            ),
        ),
    )
    origin_departure_estimated_time = db.Column(
        db.Time,
        info = dict(
            label = '',
            render_kw = dict(
                class_ = 'time-entry',
            ),
        ),
    )

    destination_station = db.Column(
        db.String,
        index = True,
        info = dict(
            label = 'Dest. Station',
        ),
    )
    destination_arrival_estimated_date = db.Column(
        db.Date,
        info = dict(
            label = 'ETA',
            render_kw = dict(
                class_ = 'date-entry',
            ),
        ),
    )
    destination_arrival_estimated_time = db.Column(
        db.Time,
        info = dict(
            label = '',
            render_kw = dict(
                class_ = 'time-entry',
            ),
        ),
    )

    @db.validates('tail_number', 'origin_station', 'destination_station')
    def uppercase(self, key, value):
        if isinstance(value, str):
            return value.upper()

    def first_truthy(self):
        for attr in ['tail_number', 'flight_number']:
            if getattr(self, attr):
                return attr


class ReportFlightBaseMixin(FlightBaseMixin):
    """
    Flights that appear on reports. Adds actual date/times and delays fields.
    """

    origin_departure_actual_date = db.Column(db.Date)
    origin_departure_actual_time = db.Column(db.Time)
    destination_arrival_actual_date = db.Column(db.Date)
    destination_arrival_actual_time = db.Column(db.Time)

    origin_delays = db.Column(db.String)
    destination_delays = db.Column(db.String)

    @db.validates('origin_delays', 'destination_delays')
    def format_delays(self, key, value):
        if isinstance(value, str):
            delays = parse.delaystring(value)
            return parse.formatdelays(delays)

    def origin_delays_objects(self):
        return parse.delaystring(self.origin_delays)

    def destination_delays_objects(self):
        return parse.delaystring(self.destination_delays)

    def controllable_destination_delays(self, over_minutes):
        """
        Controllable delays over some number of minutes.
        Return 2-tuple list of controllable delay codes > `minutes`.
        XXX: comment is wrong.
        """
        return [delay
                for delay in self.destination_delays_objects()
                if delay.is_controllable(over_minutes)]

    @property
    def is_lane(self):
        """
        Flight is a configured FlightType and its only delays are configured
        delays that are cancelled.
        """
        key = 'PERFORMANCE_LANES_INCLUDE_CANCELLED_DELAYS'
        include_cancelled_delays = current_app.config[key]
        flight_types = configured_performance_lanes_flighttypes()
        delays = self.destination_delays_objects()
        return (
            # the only delay is in the include list and is cancelled
            all(delay.code in include_cancelled_delays for delay in delays if delay.cancelled)
            and self.flight_type in flight_types
        )

    def origin_diff_minutes(self):
        est_date = self.origin_departure_estimated_date or self.report.date
        est_time = self.origin_departure_estimated_time
        act_date = self.origin_departure_actual_date or self.report.date
        act_time = self.origin_departure_actual_time
        if all([est_date, est_time, act_date, act_time]):
            est_dt = dt.datetime.combine(est_date, est_time)
            act_dt = dt.datetime.combine(act_date, act_time)
            a, b = sorted([est_dt, act_dt])
            minutes = (b - a).seconds // 60
            if est_dt >= act_dt:
                minutes *= -1
            return minutes

    def destination_diff_minutes(self):
        est_date = self.destination_arrival_estimated_date or self.report.date
        est_time = self.destination_arrival_estimated_time
        act_date = self.destination_arrival_actual_date or self.report.date
        act_time = self.destination_arrival_actual_time
        if all([est_date, est_time, act_date, act_time]):
            est_dt = dt.datetime.combine(est_date, est_time)
            act_dt = dt.datetime.combine(act_date, act_time)
            a, b = sorted([est_dt, act_dt])
            minutes = (b - a).seconds // 60
            if est_dt >= act_dt:
                minutes *= -1
            return minutes


class Flight(
    FlightTypeRelationshipMixin,
    MetaMixin,
    ReportFlightBaseMixin,
    db.Model,
):
    """
    A flight appearing on a report.
    """

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))
