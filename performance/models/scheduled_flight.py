from performance.extensions import db
from performance.models import FlightBaseMixin
from performance.models import FlightTypeRelationshipMixin
from performance.models import MetaMixin

class ScheduledFlight(
    FlightBaseMixin,
    FlightTypeRelationshipMixin,
    MetaMixin,
    db.Model,
):
    """
    Minimal flight information to partially populate new reports.

    flight_number
    leg
    tail_number
    weight
    comment
    origin_station
    origin_departure_estimated_date
    origin_departure_estimated_time
    destination_station
    destination_arrival_estimated_date
    destination_arrival_estimated_time
    flight_type
    """

    id = db.Column(db.Integer, primary_key=True)
    scheduled_report_id = db.Column(db.Integer, db.ForeignKey('scheduled_report.id'))
