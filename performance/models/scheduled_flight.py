from ..extensions import db

from .flight_mixin import FlightMixin
from .flight_type import FlightTypeRelationshipMixin
from .mixin import AppContextMixin
from .mixin import MetaMixin

class ScheduledFlight(
    AppContextMixin, # .noapp_get_or_404
                     # .noapp_pagination
    FlightMixin, # .flight_number
                 # .leg
                 # .tail_number
                 # .weight
                 # .comment
                 # .origin_station
                 # .origin_departure_estimated_date
                 # .origin_departure_estimated_time
                 # .destination_station
                 # .destination_arrival_estimated_date
                 # .destination_arrival_estimated_time
    FlightTypeRelationshipMixin, # .flight_type_id
                                 # .flight_type
                                 # .flight_type_is_lane
    MetaMixin, # .created
               # .updated
    db.Model,  # flask_sqlalchemy
):
    """
    Minimal flight information to partially populate new reports.
    """

    id = db.Column(db.Integer, primary_key=True)

    scheduled_report_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'scheduled_report.id',
            ondelete = 'CASCADE',
        ),
    )

    scheduled_report = db.relationship(
        'ScheduledReport',
        back_populates = 'scheduled_flights',
    )

    is_active = db.Column(
        db.Boolean,
        default = True,
        nullable = False,
        server_default = 'TRUE',
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

    def as_dict(self):
        """
        Return this ScheduledFlight instance as a dict.
        """
        return dict(
            id = self.id,
            is_active = self.is_active,
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
            flight_type = self.flight_type.as_dict(),
        )

    @classmethod
    def get_or_new_from_dict(cls, data):
        from .flight_type import FlightType

        instance = db.session.get(cls, dict(id=data['id']))
        if instance is None:
            instance = cls(
                id = data['id'],
                is_active = data['is_active'],
                flight_number = data['flight_number'],
                leg = data['leg'],
                tail_number = data['tail_number'],
                weight = data['weight'],
                comment = data['comment'],
                origin_station = data['origin_station'],
                origin_departure_estimated_date = data['origin_departure_estimated_date'],
                origin_departure_estimated_time = data['origin_departure_estimated_time'],
                destination_station = data['destination_station'],
                destination_arrival_estimated_date = data['destination_arrival_estimated_date'],
                destination_arrival_estimated_time = data['destination_arrival_estimated_time'],
                flight_type = FlightType.get_or_new_from_dict(data['flight_type']),
            )
        return instance
