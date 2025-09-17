from performance.extensions import db

from performance.models.mixin import AppContextMixin
from performance.models.mixin import MetaMixin
from performance.models.mixin import VisibilityMixin
from performance.models.report import Report

class ScheduledReport(
    AppContextMixin,
    MetaMixin,
    VisibilityMixin,
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

    def active_scheduled_flights(self, report_date):
        return [
            scheduled_flight.as_flight(report_date)
            for scheduled_flight in self.scheduled_flights
            if scheduled_flight.is_active
        ]

    def as_report(self, report_date):
        """
        Instantiate report from this scheduled report.
        """
        return Report(
            date = report_date,
            flights = self.active_scheduled_flights(report_date),
            show_lanes = self.show_lanes,
            show_chargeable_delays = self.show_chargeable_delays,
            show_delays_gt_30_count = self.show_delays_gt_30_count,
            show_on_time_performance_gt_15 = self.show_on_time_performance_gt_15,
            show_on_time_performance_gt_30 = self.show_on_time_performance_gt_30,
            show_flights_controllable_over_15 = self.show_flights_controllable_over_15,
            show_flights_controllable_over_30 = self.show_flights_controllable_over_30,
        )

    def as_dict(self):
        return dict(
            id = self.id,
            name = self.name,
            display_order = self.display_order,
            scheduled_flights = [
                scheduled_flight.as_dict()
                for scheduled_flight in self.scheduled_flights
            ],
            show_lanes = self.show_lanes,
            show_chargeable_delays =
                self.show_chargeable_delays,
            show_delays_gt_30_count =
                self.show_delays_gt_30_count,
            show_on_time_performance_gt_15 =
                self.show_on_time_performance_gt_15,
            show_on_time_performance_gt_30 =
                self.show_on_time_performance_gt_30,
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
                show_lanes = data['show_lanes'],
                show_chargeable_delays =
                    data['show_chargeable_delays'],
                show_delays_gt_30_count =
                    data['show_delays_gt_30_count'],
                show_on_time_performance_gt_15 =
                    data['show_on_time_performance_gt_15'],
                show_on_time_performance_gt_30 =
                    data['show_on_time_performance_gt_30'],
            )
        return instance
