from datetime import time
from operator import attrgetter

import sqlalchemy as sa

from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property

from ..extensions import db
from ..exceptions import PerformanceError
from ..models import FlightType
from ..models.mixin import MetaMixin
from ..utils import quarter_of_date

FLIGHTS_BY_TYPE_SORT = attrgetter('origin_departure_estimated_time')

class ReportError(PerformanceError):
    pass


def by_estimated_departure(flight):
    if isinstance(flight.origin_departure_estimated_time, time):
        return flight.origin_departure_estimated_time
    else:
        return time(0,0)

def flight_types_for_controllable_delays():
    """
    Return list of FlightType objects that should show controllable delays.
    """
    return FlightType.query.filter(FlightType.name == 'Scheduled').all()

def controllable_destination_delays(report, over_minutes):
    """
    Returns the controllable destination delays for a report.
    """
    # this exists to put logic in a common place for
    # `Report.controllable_destination_delays` and
    # `Report.flights_with_controllable_destination_delays` so that one can
    # return the delays and one can return the flights
    include_types = flight_types_for_controllable_delays()
    if not include_types:
        raise ReportError('List of flight types to include is empty')

    result = [
        (flight, delay)
        for flight in report.flights
        for delay in flight.controllable_destination_delays(over_minutes)
        if flight.flight_type in include_types
        and delay.is_controllable(over_minutes)
    ]
    return result

class Report(MetaMixin, db.Model):
    """
    Amazon Performance Report.
    """

    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.Date, unique=True)
    flights = db.relationship(
        'Flight',
        backref = 'report',
        cascade = 'all,delete-orphan',
    )
    system_detail = db.Column(
        db.Text,
        info = dict(
            label = 'System Detail',
        ),
    )

    @hybrid_property
    def date_quarter(self):
        """
        The quarter part of the date.
        """
        return quarter_of_date(self.date)

    @date_quarter.expression
    def date_quarter(cls):
        """
        The quarter part of the date.
        """
        # quarter of a date calculation
        # (month - 1) // 3 + 1
        # XXX: sa.func.div postgres specific
        quarter = sa.func.div(
            sa.cast(
                sa.func.date_part('month', Report.date) - 1,
                sa.Integer),
            3) + 1
        return quarter

    def flights_by_type(self):
        # [(flight_type, flight of that type), ...]
        grouped = [
            (flight_type,
             sorted(
                 (flight for flight in self.flights if flight.flight_type == flight_type),
                 key = by_estimated_departure))
            for flight_type in FlightType.query.order_by(FlightType.report_order)
        ]
        return grouped

    def lane_flights(self):
        """
        Flights in this report that are considered lanes.
        """
        return [flight for flight in self.flights if flight.is_lane]

    def controllable_destination_delays(self, over_minutes):
        """
        All report's flights controllable destination delay codes.
        """
        return [delay for flight, delay in controllable_destination_delays(self, over_minutes)]

    def flights_with_controllable_destination_delays(self, over_minutes):
        """
        """
        items = controllable_destination_delays(self, over_minutes)
        return list(set(flight for flight, delay in items))

    def flight_type_count(self, flight_type):
        """
        Return count of flights considered to be lanes.
        """
        return len([flight for flight in self.flights
                    if flight.flight_type == flight_type])
