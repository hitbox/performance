from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from wtforms_sqlalchemy.fields import QuerySelectField

from ..extensions import db

from .mixin import AppContextMixin

class FlightType(
    AppContextMixin,
    db.Model,
):
    """
    Valid types of flights. Scheduled and extra.
    """
    class Meta:
        order_by = 'report_order'

    id = db.Column(
        db.Integer,
        primary_key = True,
    )

    name = db.Column(
        db.String,
        nullable = False,
    )

    report_order = db.Column(
        db.Integer,
        default = 0,
    )

    is_controllable = db.Column(
        db.Boolean,
        nullable = False,
        server_default = 'false',
        doc = 'Include flights of this type in controllable/chargeable count.'
    )

    is_lane = db.Column(
        db.Boolean,
        nullable = False,
        server_default = 'false',
        doc = 'Include flights of this type in lane count.'
    )

    is_active = db.Column(
        db.Boolean,
        nullable = False,
        server_default = 'true',
        default = True,
        doc = 'Flight type is available for reports.',
    )

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                "'<' not supported between instances of '%s' and '%s'" %
                (type(self), type(other)))
        return self.report_order < other.report_order

    def as_dict(self):
        return dict(
            id = self.id,
            name = self.name,
            report_order = self.report_order,
            is_controllable = self.is_controllable,
            is_lane = self.is_lane,
        )

    @classmethod
    def get_or_new_from_dict(cls, data):
        """
        """
        instance = db.session.get(cls, dict(id=data['id']))
        if instance is None:
            instance = cls(
                id = data['id'],
                name = data['name'],
                report_order = data['report_order'],
                is_controllable = data['is_controllable'],
                is_lane = data['is_lane'],
            )
        return instance

    @classmethod
    def query_factory(cls):
        """
        """
        stmt = (
            db.select(FlightType)
            .where(FlightType.is_active)
            .order_by(FlightType.report_order)
        )
        return db.session.scalars(stmt)

    @classmethod
    def as_query_select_field(cls, **kwargs):
        """
        """
        kwargs.setdefault('label', 'Flight Type')
        kwargs.setdefault('get_label', 'name')
        kwargs.setdefault('query_factory', cls.query_factory)

        render_kw = kwargs.setdefault('render_kw', {})
        render_kw.setdefault('class', 'narrower flight')
        render_kw.setdefault('autofocus', True)

        field = QuerySelectField(**kwargs)
        return field


class FlightTypeRelationshipMixin:
    """
    Mixin adds a relationship to FlightType.
    """

    @declared_attr
    def flight_type_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey('flight_type.id'),
            info = dict(
                # wtforms_alchemy: the existance of 'choices' key with a truthy
                # value causes SelectField
                choices = [0],
            )
        )

    @declared_attr
    def flight_type(cls):
        return db.relationship(FlightType, uselist=False)

    @declared_attr
    def flight_type_is_lane(cls):
        return association_proxy('flight_type', 'is_lane')
