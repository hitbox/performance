from performance.extensions import db
from performance.models import FlightBaseMixin
from performance.models import FlightTypeRelationshipMixin
from performance.models import MetaMixin
from performance.models import ReportFlightBaseMixin

from .bound import BoundRelationshipMixin
from .operation import OperationRelationshipMixin

class Flight(
    BoundRelationshipMixin,
    FlightTypeRelationshipMixin,
    MetaMixin,
    OperationRelationshipMixin,
    ReportFlightBaseMixin,
    db.Model,
):

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id', ondelete='CASCADE'))
