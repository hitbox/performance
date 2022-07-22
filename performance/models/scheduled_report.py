from performance.extensions import db

from .mixin import AppContextMixin
from .mixin import MetaMixin

class ScheduledReport(
    AppContextMixin,
    MetaMixin,
    db.Model,
):
    """
    Scheduled reports hold minimal flights to populate new reports on the
    effective datetime start.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    display_order = db.Column(db.Integer)

    scheduled_flights = db.relationship(
        'ScheduledFlight',
        back_populates = 'scheduled_report',
        # ETD seems more logical but it's been flight_number for a long time.
        #order_by = 'ScheduledFlight.origin_departure_estimated_time',
        order_by = ','.join([
            'ScheduledFlight.flight_number',
            'ScheduledFlight.origin_departure_estimated_time',
        ]),
    )

    def as_report(self, report_date):
        """
        Instantiate report from this scheduled report.
        """
        from .report import Report
        return Report(
            date = report_date,
            flights = [
                scheduled_flight.as_flight()
                for scheduled_flight in self.scheduled_flights
            ],
        )
