from ..extensions import db

from .flight_mixin import FlightMixin
from .flight_type import FlightTypeRelationshipMixin
from .mixin import AppContextMixin
from .mixin import MetaMixin

class ScheduledFlight(
    AppContextMixin,
    FlightMixin,
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

    scheduled_report_id = db.Column(
        db.Integer,
        db.ForeignKey('scheduled_report.id'),
    )

    scheduled_report = db.relationship(
        'ScheduledReport',
        back_populates = 'scheduled_flights',
    )

    def as_flight(self):
        """
        Instantiate flight from this scheduled flight.
        """
        from .flight import Flight
        return Flight(
            flight_number = self.flight_number,
            leg = self.leg,
            tail_number = self.tail_number,
            weight = self.weight,
            comment = self.comment,
            origin_station = self.origin_station,
            origin_departure_estimated_date = self.origin_departure_estimated_date,
            origin_departure_estimated_time = self.origin_departure_estimated_time,
            destination_station = self.destination_station,
            destination_arrival_estimated_date = self.destination_arrival_estimated_date,
            destination_arrival_estimated_time = self.destination_arrival_estimated_time,
            flight_type = self.flight_type,
        )
