from ...extensions import db
from ...models import FlightBaseMixin
from ...models import FlightTypeRelationshipMixin
from ...models import MetaMixin

from .bound import BoundRelationshipMixin
from .operation import OperationRelationshipMixin

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
