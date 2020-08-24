from sqlalchemy.ext.declarative import declared_attr

from ...extensions import db
from ...models.mixin import MetaMixin

class Bound(
    db.Model,
    MetaMixin,
):
    """
    Created to allow an additional relationship to flights for in/out bound.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    altname = db.Column(db.String)


class BoundRelationshipMixin:

    @declared_attr
    def bound_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey('bound.id'),
        )

    @declared_attr
    def bound(cls):
        return db.relationship(Bound)
