from sqlalchemy.ext.hybrid import hybrid_property

from performance.exceptions import PerformanceError
from performance.extensions import db
from performance.utils import quarter_of_date

from .assumed_best import AssumedBest
from .flight import FlightType
from .mixin import MetaMixin
from .mixin import VisibilityMixin

class ReportError(PerformanceError):
    pass


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

class Report(
    MetaMixin,
    VisibilityMixin,
    db.Model,
):
    """
    Amazon Performance Report.
    """

    id = db.Column(
        db.Integer,
        primary_key = True,
    )

    date = db.Column(
        db.Date,
        unique = True,
    )

    flights = db.relationship(
        'Flight',
        back_populates = 'report',
        cascade = 'all, delete-orphan',
    )

    system_detail = db.Column(
        db.Text,
        info = dict(
            label = 'System Detail',
        ),
    )

    @hybrid_property
    def assumed_best(self):
        # XXX: not quite sure this is a great way to do this, but I want this
        #      attribute on report objects
        ident = dict(
            month = self.date.month,
            year = self.date.year,
        )
        instance = db.session.get(AssumedBest, ident)
        return instance

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
        # NOTE: db.func.div postgres specific
        zero_based_month = db.cast(
            db.func.date_part('month', Report.date) - 1,
            db.Integer
        )
        quarter = 1 + db.func.div(zero_based_month, 3)
        return quarter

    def flights_by_type(self):
        """
        Group flights for this report by FlightType and sort the groups of
        flights by ETD.
        """
        from .flight import Flight

        groups = []
        stmt = (
            db.select(FlightType)
            .where(FlightType.is_active)
            .order_by(FlightType.report_order)
        )
        for flight_type in db.session.scalars(stmt):
            stmt = (
                db.select(Flight)
                .join(Report)
                .where(
                    Report.id == self.id,
                    Flight.flight_type_id == flight_type.id,
                )
                .order_by(Flight.origin_departure_estimated_time_or_midnight)
            )
            flights = db.session.scalars(stmt).all()
            groups.append((flight_type, flights))
        return groups

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

    def controllable_over_minutes_columns(self):
        """
        Return list of over-minutes columns configured for report.
        """
        columns = []
        if self.show_flights_controllable_over_15:
            columns.append(
                self.__class__.show_flights_controllable_over_15.info['table_header'],
            )
        if self.show_flights_controllable_over_30:
            columns.append(
                self.__class__.show_flights_controllable_over_30.info['table_header'],
            )
        return columns

    def controllable_over_minutes_values(self, flight):
        """
        Return list of over-minutes values (matching the columns) configured
        for report.
        """
        values = []
        if self.show_flights_controllable_over_15:
            is_over = flight.controllable_destination_delays_minutes > 15
            values.append(is_over)
        if self.show_flights_controllable_over_30:
            is_over = flight.controllable_destination_delays_minutes > 30
            values.append(is_over)
        return values
