from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property

from .. import parse
from ..extensions import db

from .delay import Delay
from .mixin import UniqueMixin

class DelayAssocMixin(UniqueMixin):
    """
    Common attributes for origin/destination delays associated with a flight.
    """

    @db.declared_attr
    def flight_id(cls):
        """
        Foreign key column to flight table.
        """
        return db.Column(db.ForeignKey('flight.id'), primary_key=True)

    @db.declared_attr
    def delay_id(cls):
        """
        Foreign key column to delay table.
        """
        return db.Column(db.ForeignKey('delay.id'), primary_key=True)

    @db.declared_attr
    def position(cls):
        """
        Position (order) of flight delay.
        """
        return db.Column(db.Integer, primary_key=True)

    @db.declared_attr
    def delay_object(cls):
        """
        Attribute to delay object itself.
        """
        return db.relationship(Delay)

    @db.declared_attr
    def code(cls):
        """
        Convenience attribute for the delay code string.
        """
        return association_proxy(
            'delay_object',
            'code',
            creator = lambda code: Delay.as_unique(db.session, code=code)
        )

    @db.declared_attr
    def is_controllable(cls):
        """
        Convenient access to .delay_object.is_controllable
        """
        return association_proxy('delay_object', 'is_controllable')

    @db.declared_attr
    def is_cancelled_lane(cls):
        """
        Convenient access to .delay_object.is_cancelled_lane
        """
        return association_proxy('delay_object', 'is_cancelled_lane')

    @db.declared_attr
    def minutes(cls):
        """
        Minutes associated with delay code.
        """
        return db.Column(db.Integer)

    @hybrid_property
    def minutes_formatted(self):
        """
        Nicely formatted minutes for delay code.
        """
        return parse.string_for_minutes(self.minutes)

    @minutes_formatted.expression
    def minutes_formatted(cls):
        """
        SQL side: minutes_formatted
        """
        return db.case(
            (cls.minutes != None, db.func.concat('(', cls.minutes, ')')),
            else_ = '')

    @db.declared_attr
    def is_cancelled(cls):
        """
        This code is the one that cancelled this flight.
        """
        return db.Column(db.Boolean, nullable=False, server_default='false')

    @hybrid_property
    def is_cancelled_formatted(self):
        """
        Formatted string for is_cancelled
        """
        return parse.string_for_cancelled(self.is_cancelled)

    @is_cancelled_formatted.expression
    def is_cancelled_formatted(cls):
        """
        SQL side: is_cancelled_formatted
        """
        return db.case(
            (cls.is_cancelled, f'{parse.CANCELLED} '),
            else_ = ''
        )

    @hybrid_property
    def formatted(self):
        """
        Nicely formatted string for this flight delay code.
        """
        return parse.format_delay(self.code, self.minutes, self.is_cancelled)

    @formatted.expression
    def formatted(cls):
        """
        SQL side: formatted
        """
        return db.func.concat(
            cls.is_cancelled_formatted,
            Delay.query
                 .with_entities(Delay.code)
                 .filter(Delay.id == cls.delay_id)
                 .scalar_subquery(),
            cls.minutes_formatted,
        )

    @classmethod
    def unique_hash(cls, *, flight_id, delay_id, position):
        """
        Return hashable object to uniquely identify a flight delay.
        """
        if cls is DelayAssocMixin:
            raise NotImplementedError(
                'unique_hash should never be called from %s' % cls)
        return (flight_id, delay_id, position)

    @classmethod
    def unique_filter(cls, query, *, flight_id, delay_id, position):
        """
        Fix up query with criteria to retrieve instance from database.
        """
        if cls is DelayAssocMixin:
            raise NotImplementedError(
                'unique_filter should never be called from %s' % cls)
        return cls.query.filter(
            cls.flight_id == flight_id,
            cls.delay_id == delay_id,
            cls.position == position,
        )


class OriginDelay(
    DelayAssocMixin,
    db.Model,
):
    """
    Origin delay
    """

    flight = db.relationship(
        'Flight',
        back_populates = 'origin_delays',
    )


class DestinationDelay(
    DelayAssocMixin,
    db.Model,
):
    """
    Destination delay
    """

    flight = db.relationship(
        'Flight',
        back_populates = 'destination_delays',
    )
