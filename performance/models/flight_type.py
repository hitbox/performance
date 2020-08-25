from sqlalchemy.ext.declarative import declared_attr

from ..extensions import db

class FlightType(db.Model):
    """
    Valid types of flights. Scheduled and extra.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    report_order = db.Column(db.Integer, default=0)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                "'<' not supported between instances of '%s' and '%s'" %
                (type(self), type(other)))
        return self.report_order < other.report_order


class FlightTypeRelationshipMixin:

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
        return db.relationship(FlightType)
