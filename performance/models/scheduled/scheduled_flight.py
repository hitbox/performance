from datetime import date
from datetime import timedelta

from performance.extensions import db

from performance.models.flight import FlightMixin
from performance.models.flight import FlightTypeRelationshipMixin
from performance.models.mixin import AppContextMixin
from performance.models.mixin import MetaMixin

class ScheduledFlight(
    AppContextMixin,
    FlightMixin,
    FlightTypeRelationshipMixin,
    MetaMixin,
    db.Model,
):
    """
    Minimal flight information to partially populate new reports.
    """
    class Meta:
        paginate_kw = dict(
            per_page = 10,
        )


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

    origin_departure_estimated_date_template = db.Column(
        db.String,
        nullable = True,
        doc = 'Format string for ISO format date.',
    )

    destination_arrival_estimated_date_template = db.Column(
        db.String,
        nullable = True,
        doc = 'Format string for ISO format date.',
    )

    is_active = db.Column(
        db.Boolean,
        default = True,
        nullable = False,
        server_default = 'TRUE',
        doc = 'Flight is loaded on new operation.',
    )

    @staticmethod
    def resolve_date(literal, string_or_none, **context):
        if literal:
            return literal

        if string_or_none:
            string_or_none = string_or_none.strip()
            if string_or_none:
                date_string = string_or_none.format(**context)
                date_value = date.fromisoformat(date_string)
                return date_value

    def resolve_estimated_departure_date(self, **context):
        return self.resolve_date(
            self.origin_departure_estimated_date,
            self.origin_departure_estimated_date_template,
            **context
        )

    def resolve_estimated_arrival_date(self, **context):
        return self.resolve_date(
            self.destination_arrival_estimated_date,
            self.destination_arrival_estimated_date_template,
            **context
        )

    @staticmethod
    def context_for_dates(report_date):
        context = {
            'report_date': report_date,
            'one_day': timedelta(days=1),
            'date+1': report_date + timedelta(days=1),
            'date-1': report_date - timedelta(days=1),
        }
        return context

    def as_flight(self, report_date):
        """
        Instantiate flight from this scheduled flight.
        """
        from performance.models.flight import Flight

        context = self.context_for_dates(report_date)
        origin_departure_estimated_date = self.resolve_estimated_departure_date(**context)
        destination_arrival_estimated_date = self.resolve_estimated_arrival_date(**context)

        return Flight(
            flight_number = self.flight_number,
            leg = self.leg,
            tail_number = self.tail_number,
            weight = self.weight,
            comment = self.comment,
            origin_station = self.origin_station,
            origin_departure_estimated_date = origin_departure_estimated_date,
            origin_departure_estimated_time = self.origin_departure_estimated_time,
            destination_station = self.destination_station,
            destination_arrival_estimated_date = destination_arrival_estimated_date,
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
        from performance.models.flight import FlightType

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
