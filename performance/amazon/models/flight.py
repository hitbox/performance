from performance.extensions import db
from performance.models import FlightTypeRelationshipMixin
from performance.models import MetaMixin
from performance.models import ReportFlightBaseMixin

class Flight(
    FlightTypeRelationshipMixin,
    MetaMixin,
    ReportFlightBaseMixin,
    db.Model,
):

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))
