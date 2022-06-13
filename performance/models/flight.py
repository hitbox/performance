import datetime as dt
import string

from flask import current_app

from .. import parse
from ..extensions import db
from ..types import DelayCodesType

from .flight_type import FlightTypeRelationshipMixin
from .mixin import MetaMixin

def configured_performance_lanes_flighttypes():
    """
    The FlightType's that count for lanes.
    """
    from .flight_type import FlightType
    flight_types_names = current_app.config['PERFORMANCE_LANES_FLIGHTTYPES']
    flight_types = FlightType.query.filter(FlightType.name.in_(flight_types_names)).all()
    return flight_types

def configured_include_cancelled_delays():
    """
    The required, configured delay codes to include in counting lanes.
    """
    return current_app.config['PERFORMANCE_LANES_INCLUDE_CANCELLED_DELAYS']

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
        """
        Hacky function to return first truthy attribute name for use in making
        the edit link. Maybe this should be a template macro?
        """
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

    origin_delays = db.Column(DelayCodesType)
    destination_delays = db.Column(DelayCodesType)

    def controllable_destination_delays(self, over_minutes):
        """
        Controllable delays over some number of minutes.
        Return 2-tuple list of controllable delay codes > `minutes`.
        XXX: comment is wrong.
        """
        return [delay
                for delay in self.destination_delays
                if delay.is_controllable(over_minutes)]

    @property
    def is_lane(self):
        """
        Flight is a configured FlightType and its only delays are configured
        delays that are cancelled.
        """
        include_cancelled_delays = configured_include_cancelled_delays()
        flight_types = configured_performance_lanes_flighttypes()
        delays = self.destination_delays
        return (
            # the only delay is in the include list and is cancelled
            all(delay.code in include_cancelled_delays
                for delay in delays
                if delay.cancelled)
            and self.flight_type in flight_types
        )

    def origin_diff_minutes(self):
        """
        Destination diff est./act. minutes; possibly None.
        """
        minutes = diff_minutes(
            self.origin_departure_estimated_date or self.report.date,
            self.origin_departure_estimated_time,
            self.origin_departure_actual_date or self.report.date,
            self.origin_departure_actual_time,
        )
        return minutes

    def origin_diff_minutes_value(self):
        """
        Ensure a value for origin diff minutes.
        """
        return self.origin_diff_minutes() or 0

    def show_origin_delays(self):
        """
        Return True that origin delays should show.
        """
        return should_show_delays(
            self.origin_diff_minutes_value(),
            self.origin_delays
        )

    def destination_diff_minutes(self):
        """
        Destination diff est./act. minutes; possibly None.
        """
        minutes = diff_minutes(
            self.destination_arrival_estimated_date or self.report.date,
            self.destination_arrival_estimated_time,
            self.destination_arrival_actual_date or self.report.date,
            self.destination_arrival_actual_time,
        )
        return minutes

    def destination_diff_minutes_value(self):
        """
        Ensure a value for destination diff minutes.
        """
        return self.destination_diff_minutes() or 0

    def show_destination_delays(self):
        """
        Return True that destination delays should show.
        """
        return should_show_delays(
            self.destination_diff_minutes_value(),
            self.destination_delays
        )


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


def diff_minutes(est_date, est_time, act_date, act_time):
    """
    If all truthy, calculate the difference in minute between estimated and
    actual dates and times.
    """
    if all([est_date, est_time, act_date, act_time]):
        est_dt = dt.datetime.combine(est_date, est_time)
        act_dt = dt.datetime.combine(act_date, act_time)
        a, b = sorted([est_dt, act_dt])
        minutes = int((b - a).total_seconds()) // 60
        if est_dt > act_dt:
            minutes *= -1
        return minutes

def should_show_delays(diff_minutes, delays):
    """
    Return whether the delay codes should be shown.
    """
    late_gt = current_app.config['LATE_GT']
    always_show_delay_cods = current_app.config['ALWAYS_SHOW_DELAY_CODES']
    return (
        diff_minutes > late_gt
        or any(delay.cancelled or delay.code in always_show_delay_cods for delay in delays)
    )
