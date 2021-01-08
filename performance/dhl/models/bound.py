from sqlalchemy.ext.declarative import declared_attr

from performance.extensions import db
from performance.models.mixin import MetaMixin

class Bound(db.Model, MetaMixin):
    """
    Created to allow an additional relationship to flights for in/out bound.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    altname = db.Column(db.String)
    report_order = db.Column(db.Integer, default=0)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError(
                "'<' not supported between instances of '%s' and '%s'" %
                (type(self), type(other)))
        return self.report_order < other.report_order


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
