import datetime

from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list

from performance import parse
from performance import settings
from performance.extensions import db
from performance.utils import diff_minutes

from .delay import Delay
from .flight_delay import DestinationDelay
from .flight_delay import OriginDelay
from .flight_mixin import FlightMixin
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
    report_id = db.Column(
        db.ForeignKey('report.id'),
        nullable = False,
    )
    report = db.relationship(
        'Report',
        back_populates = 'flights',
    )

    origin_departure_actual_date = db.Column(
        db.Date,
        info = dict(
            label = 'ATD Date',
        ),
    )

    origin_departure_actual_time = db.Column(
        db.Time,
        info = dict(
            label = 'ATD Time',
        ),
    )

    destination_arrival_actual_date = db.Column(
        db.Date,
        info = dict(
            label = 'ATA Date',
        ),
    )

    destination_arrival_actual_time = db.Column(
        db.Time,
        info = dict(
            label = 'ATA Time',
        ),
    )

    origin_delays = db.relationship(
        'OriginDelay',
        cascade = 'all, delete-orphan',
        collection_class = ordering_list('position'),
        order_by = 'OriginDelay.position',
    )

    destination_delays = db.relationship(
        'DestinationDelay',
        cascade = 'all, delete-orphan',
        collection_class = ordering_list('position'),
        order_by = 'DestinationDelay.position',
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
            session = db.session,
            delays_string = delay_codes_string,
            delays_list = self.origin_delays,
            flight_delay_class = OriginDelay,
            flight_id = self.id,
            flight = self,
            attr = 'origin_delays',
        )

    @origin_delays_string.expression
    def origin_delays_string(cls):
        """
        SQL side of origin_delays_string
        """
        return sql_delays_string(cls, OriginDelay)

    @hybrid_property
    def origin_departure_estimated_datetime(self):
        return datetime.datetime.combine(
            self.origin_departure_estimated_date or self.report.date,
            self.origin_departure_estimated_time,
        )

    @origin_departure_estimated_datetime.expression
    def origin_departure_estimated_datetime(cls):
        return (
            cls.origin_departure_estimated_date
            + db.func.cast(
                self.origin_departure_estimated_time,
                db.func.Interval(second_precision=True),
            )
        )

    @hybrid_property
    def origin_departure_actual_datetime(self):
        return datetime.datetime.combine(
            self.origin_departure_actual_date or self.report.date,
            self.origin_departure_actual_time,
        )

    @origin_departure_actual_datetime.expression
    def origin_departure_actual_datetime(cls):
        return (
            cls.origin_departure_actual_date
            + db.func.cast(
                self.origin_departure_actual_time,
                db.func.Interval(second_precision=True),
            )
        )

    @hybrid_property
    def destination_arrival_actual_datetime(self):
        return datetime.datetime.combine(
            self.destination_arrival_actual_date or self.report.date,
            self.destination_arrival_actual_time,
        )

    @destination_arrival_actual_datetime.expression
    def destination_arrival_actual_datetime(cls):
        return (
            cls.destination_arrival_actual_date
            + db.func.cast(
                self.destination_arrival_actual_time,
                db.func.Interval(second_precision=True),
            )
        )

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
            session = db.session,
            delays_string = delay_codes_string,
            delays_list = self.destination_delays,
            flight_delay_class = DestinationDelay,
            flight_id = self.id,
            flight = self,
            attr = 'destination_delays',
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
            and destination_delay.delay.is_controllable
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
                destination_delay.delay.is_cancelled_lane
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
    flight_id,
    flight,
    attr,
    ignore_codes = None,
):
    """
    Ensure that the delay codes scraped from text input exists as database
    objects for linking through the association objects. Ignores the
    unaccounted minutes placeholder.
    """
    if ignore_codes is None:
        ignore_codes = set()
    list_ = []
    delays = parse.delaystring(delays_string)
    for position, delay_data in enumerate(delays):
        # ignore placeholder
        if delay_data['code'] in ignore_codes:
            continue
        # add delay object if needed
        stmt = db.select(Delay).where(
            Delay.code == delay_data['code'],
        )
        delay = session.scalars(stmt).one_or_none()
        if delay is None:
            delay = Delay(code = delay_data['code'])
            session.add(delay)
        # append association object
        assoc = flight_delay_class(
            flight = flight,
            delay = delay,
            position = position,
            minutes = delay_data['minutes'],
            is_cancelled = delay_data['is_cancelled'],
        )
        list_.append(assoc)
    setattr(flight, attr, list_)
    session.commit()

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
