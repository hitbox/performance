import string

from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list

from .. import parse
from ..extensions import db
from ..utils import diff_minutes

from .delay import Delay
from .flight_delay import DestinationDelay
from .flight_delay import OriginDelay
from .flight_mixin import FlightMixin
from .flight_type import FlightType
from .flight_type import FlightTypeRelationshipMixin
from .mixin import MetaMixin

class Flight(
    FlightMixin,
    FlightTypeRelationshipMixin,
    MetaMixin,
    db.Model,
):
    """
    A flight appearing on a report. Mainly adds actual date/times and delay codes.
    """

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.ForeignKey('report.id'))

    origin_departure_actual_date = db.Column(db.Date)
    origin_departure_actual_time = db.Column(db.Time)
    destination_arrival_actual_date = db.Column(db.Date)
    destination_arrival_actual_time = db.Column(db.Time)

    # origin_delays #

    @db.declared_attr
    def origin_delays(cls):
        """
        Origin delay objects.
        """
        return db.relationship(
            'OriginDelay',
            cascade = 'all, delete-orphan',
            collection_class = ordering_list('position'),
            order_by = 'OriginDelay.position',
        )

    @hybrid_property
    def origin_delays_string(self):
        """
        Return this flights origin delays as formatted string.
        """
        return ' '.join(origin_delay.formatted for origin_delay in self.origin_delays)

    @origin_delays_string.setter
    def origin_delays_string(self, delay_codes_string):
        """
        Convert/parse delay codes string into a list of OriginDelay objects and
        set origin_delays attribute.
        """
        delays_setter(
            db.session,
            delay_codes_string,
            self.origin_delays,
            OriginDelay,
            self.id,
        )

    @origin_delays_string.expression
    def origin_delays_string(cls):
        """
        SQL side of origin_delays_string
        """
        return sql_delays_string(cls, OriginDelay)

    def origin_diff_minutes(self):
        """
        Origin departure time difference between estimated and actual in
        absolute minutes; possibly None.
        """
        minutes = diff_minutes(
            self.origin_departure_estimated_date or self.report.date,
            self.origin_departure_estimated_time,
            self.origin_departure_actual_date or self.report.date,
            self.origin_departure_actual_time,
        )
        return minutes

    def origin_diff_minutes_value(self):
        """
        Ensure a value for origin diff minutes.
        """
        return self.origin_diff_minutes() or 0

    def show_origin_delays(self):
        """
        Return True that origin delays should show.
        """
        return should_show_delays(
            self.origin_diff_minutes_value(),
            self.origin_delays
        )

    # destination_delays #

    @db.declared_attr
    def destination_delays(cls):
        """
        Destination delay objects.
        """
        return db.relationship(
            'DestinationDelay',
            cascade = 'all, delete-orphan',
            collection_class = ordering_list('position'),
            order_by = 'DestinationDelay.position',
        )

    @hybrid_property
    def destination_delays_string(self):
        """
        Return this flights destination delays as formatted string.
        """
        return ' '.join(delay.formatted for delay in self.destination_delays)

    @destination_delays_string.setter
    def destination_delays_string(self, delay_codes_string):
        """
        Convert/parse delay codes string into a list of DestinationDelay
        objects and set destination_delays attribute.
        """
        delays_setter(
            db.session,
            delay_codes_string,
            self.destination_delays,
            DestinationDelay,
            self.id,
        )

    @destination_delays_string.expression
    def destination_delays_string(cls):
        """
        SQL side of destination_delays_string
        """
        return sql_delays_string(cls, DestinationDelay)

    def destination_diff_minutes(self):
        """
        Destination diff est./act. minutes; possibly None.
        """
        minutes = diff_minutes(
            self.destination_arrival_estimated_date or self.report.date,
            self.destination_arrival_estimated_time,
            self.destination_arrival_actual_date or self.report.date,
            self.destination_arrival_actual_time,
        )
        return minutes

    def destination_diff_minutes_value(self):
        """
        Ensure a value for destination diff minutes.
        """
        return self.destination_diff_minutes() or 0

    def show_destination_delays(self):
        """
        Return True that destination delays should show.
        """
        return should_show_delays(
            self.destination_diff_minutes_value(),
            self.destination_delays
        )

    @hybrid_property
    def controllable_destination_delays_minutes(self):
        """
        Total controllable destination delays' minutes.
        """
        return sum(
            destination_delay.minutes
            for destination_delay in self.destination_delays
            if destination_delay.minutes is not None
            and destination_delay.delay_object.is_controllable
        )

    @controllable_destination_delays_minutes.expression
    def controllable_destination_delays_minutes(self):
        """
        Total controllable destination delays' minutes as subquery.
        """
        return (DestinationDelay
            .query
            .join(Delay)
            .with_entities(
                db.func.sum(DestinationDelay.minutes),
            ).filter(
                Flight.id == DestinationDelay.flight_id,
                Delay.is_controllable,
            ).scalar_subquery())

    # other #

    @hybrid_property
    def is_lane(self):
        """
        Does this flight count as lane?
        """
        return (
            self.flight_type.is_lane
            # all cancelled delays are permitted by flag on delay object
            and all(
                destination_delay.delay_object.is_cancelled_lane
                for destination_delay in self.destination_delays
                if destination_delay.is_cancelled
            ))

    @is_lane.expression
    def is_lane(cls):
        """
        SQL side, does this flight count as lane?
        """
        return db.and_(
            # our FlightType is counted as lanes
            # (equals true is required by the association proxy, I think)
            cls.flight_type_is_lane == True,
            # we DO NOT have...
            db.not_(
                # ...a destination delay...
                DestinationDelay
                .query
                .filter(
                    DestinationDelay.flight_id == cls.id,
                    # ...that is cancelled
                    DestinationDelay.is_cancelled,
                    # and not counted as a lane when cancelled
                    DestinationDelay.is_cancelled_lane == False,
                ).exists()
            ))


def configured_performance_lanes_flighttype_names():
    # TODO: move stuff like this to config.py?
    flight_types_names = current_app.config['PERFORMANCE_LANES_FLIGHTTYPES']
    return flight_types_names

_configured_performance_lanes_flighttypes = None

def configured_performance_lanes_flighttypes():
    """
    The FlightType's that count for lanes.
    """
    global _configured_performance_lanes_flighttypes
    if _configured_performance_lanes_flighttypes is not None:
        return _configured_performance_lanes_flighttypes
    from .flight_type import FlightType
    flight_types_names = current_app.config['PERFORMANCE_LANES_FLIGHTTYPES']
    flight_types = FlightType.query.filter(FlightType.name.in_(flight_types_names)).all()
    _configured_performance_lanes_flighttypes = flight_types
    return _configured_performance_lanes_flighttypes

_configured_include_cancelled_delays = None

def configured_include_cancelled_delays():
    """
    The required, configured delay codes to include in counting lanes.
    """
    global _configured_include_cancelled_delays
    if _configured_include_cancelled_delays is not None:
        return _configured_include_cancelled_delays
    key = 'PERFORMANCE_LANES_INCLUDE_CANCELLED_DELAYS'
    _configured_include_cancelled_delays = current_app.config[key]
    return _configured_include_cancelled_delays

def should_show_delays(diff_minutes, delays):
    """
    Return whether the delay codes should be shown.
    """
    late_gt = current_app.config['LATE_GT']
    always_show_delay_cods = current_app.config['ALWAYS_SHOW_DELAY_CODES']
    return (
        diff_minutes > late_gt
        or any(
            delay.is_cancelled or delay.code in always_show_delay_cods
            for delay in delays
        )
    )

def delays_setter(
    session,
    delays_string,
    delays_list,
    flight_delay_class,
    flight_id
):
    """
    Generic function to clear and update the flight delays list.
    """
    delays_data = parse.delaystring(delays_string)
    delays_list.clear()
    for position, delay_data in enumerate(delays_data):
        # see flask_sqlalchemy.SQLAlchemy(session_options=...)
        # not sure why this should happen anyway but the unique object pattern
        # from (actual) SQLAlchemy do not seem compatible on this.
        delay_code = Delay.as_unique(session, code=delay_data['code'])
        if delay_code.id is None:
            # new
            flight_delay = flight_delay_class(
                flight_id = flight_id,
                delay_object = delay_code,
                position = position,
            )
        else:
            # lookup from cache or database, or create
            flight_delay = flight_delay_class.as_unique(
                session,
                flight_id = flight_id,
                delay_id = delay_code.id,
                position = position,
            )
        flight_delay.minutes = delay_data['minutes']
        delays_list.append(flight_delay)

def sql_delays_string(cls, flight_delay_class):
    if db.engine.dialect.name != 'postgresql':
        raise NotImplementedError
    query = cls.query.join(
        flight_delay_class
    ).with_entities(
        # postgres way of joining rows on a separator
        db.func.string_agg(flight_delay_class.formatted, ' ')
    ).scalar_subquery()
    return query
