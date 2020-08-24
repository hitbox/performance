import datetime as dt

from flask import current_app

from ... import parse
from ...extensions import db
from ...models import FlightBaseMixin
from ...models import FlightTypeRelationshipMixin
from ...models import MetaMixin
from ...models import ReportFlightBaseMixin

from .bound import BoundRelationshipMixin
from .operation import OperationRelationshipMixin

class Flight(
    BoundRelationshipMixin,
    ReportFlightBaseMixin,
    FlightTypeRelationshipMixin,
    MetaMixin,
    OperationRelationshipMixin,
    db.Model,
):

    id = db.Column(db.Integer, primary_key=True)

    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))

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
        if self.origin_delays:
            items.extend(parse.delaystring(self.origin_delays))
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


class ScheduledFlight(
    BoundRelationshipMixin,
    FlightBaseMixin,
    FlightTypeRelationshipMixin,
    MetaMixin,
    db.Model,
):
    """
    Minimal flight information to partially populate new reports.
    """

    id = db.Column(db.Integer, primary_key=True)

    scheduled_report_id = db.Column(db.Integer, db.ForeignKey('scheduled_report.id'))
