from sqlalchemy.ext.declarative import declared_attr

from ...extensions import db
from ...models import MetaMixin

class Operation(
    MetaMixin,
    db.Model,
):
    """
    A named operation.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class OperationRelationshipMixin:

    @declared_attr
    def operation_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey('operation.id'),
            info = dict(
                # wtforms_alchemy: the existance of 'choices' key with a truthy
                # value causes SelectField
                choices = [0],
            )
        )

    @declared_attr
    def operation(cls):
        return db.relationship(Operation)
