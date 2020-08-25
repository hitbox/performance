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


class ScheduledFlight(
    BoundRelationshipMixin,
    FlightBaseMixin,
    FlightTypeRelationshipMixin,
    MetaMixin,
    OperationRelationshipMixin,
    db.Model,
):
    """
    Minimal flight information to partially populate new reports.
    """

    id = db.Column(db.Integer, primary_key=True)

    scheduled_report_id = db.Column(db.Integer, db.ForeignKey('scheduled_report.id'))
