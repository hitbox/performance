import datetime as dt
import string

from flask import current_app

from .. import parse
from ..extensions import db

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
            return parse.formatdelays(parse.delaystring(value))

    def controllable_over(self, minutes):
        """
        Controllable delays over some number of minutes.
        Return 2-tuple list of controllable delay codes > `minutes`.
        """
        controllable_codes = current_app.config['PERFORMANCE_CONTROLLABLE']
        items = []
        # XXX: confirm it's only destination delays that count
        #if self.origin_delays:
        #    items.extend(parse.delaystring(self.origin_delays))
        if self.destination_delays:
            items.extend(parse.delaystring(self.destination_delays))
        items = [(code, delay_minutes)
                 for code, delay_minutes in items
                 if code in controllable_codes
                 and delay_minutes
                 and delay_minutes > minutes]
        return items

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
