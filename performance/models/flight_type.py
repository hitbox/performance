from sqlalchemy.ext.declarative import declared_attr

from ..extensions import db

class FlightType(db.Model):
    """
    Valid types of flights. Scheduled and extra.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    order = db.Column(db.Integer)


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
