from performance.extensions import db

from .mixin import AppContextMixin
from .mixin import MetaMixin
from .report import Report

class ScheduledReport(
    AppContextMixin,
    MetaMixin,
    db.Model,
):
    """
    Scheduled reports hold minimal flights to populate new reports on the
    effective datetime start.
    """
    class Meta:
        order_by = 'display_order'


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    display_order = db.Column(db.Integer)

    scheduled_flights = db.relationship(
        'ScheduledFlight',
        back_populates = 'scheduled_report',
        cascade = 'all, delete-orphan',
        order_by = ','.join([
            'ScheduledFlight.origin_departure_estimated_time',
            'ScheduledFlight.flight_number_as_integer',
        ]),
    )

    def as_report(self, report_date):
        """
        Instantiate report from this scheduled report.
        """
        return Report(
            date = report_date,
            flights = [
                scheduled_flight.as_flight()
                for scheduled_flight in self.scheduled_flights
                if scheduled_flight.is_active
            ],
        )

    def as_dict(self):
        return dict(
            id = self.id,
            name = self.name,
            display_order = self.display_order,
            scheduled_flights = [
                scheduled_flight.as_dict()
                for scheduled_flight in self.scheduled_flights
            ]
        )

    @classmethod
    def get_or_new_from_dict(cls, data):
        from .scheduled_flight import ScheduledFlight

        instance = db.session.get(cls, dict(id=data['id']))
        if instance is None:
            instance = cls(
                id = data['id'],
                name = data['name'],
                display_order = data['display_order'],
                scheduled_flights = [
                    ScheduledFlight.get_or_new_from_dict(flight_data)
                    for flight_data in data['scheduled_flights']
                ],
            )
        return instance
