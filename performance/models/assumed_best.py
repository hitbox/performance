from datetime import time
from operator import attrgetter

import sqlalchemy as sa

from performance.extensions import db
from .mixin import MetaMixin
from .mixin import AppContextMixin

class AssumedBest(
    AppContextMixin,
    MetaMixin,
    db.Model,
):
    """
    Assumed best performance number for a month.
    """

    id = db.Column(db.Integer, primary_key=True)

    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    lanes = db.Column(db.Integer, info=dict(label='Lanes'))

    @db.validates('month')
    def validate_month(self, key, value):
        if not 0 < value < 13:
            raise ValueError('month must be between 1 and 12.')
        return value
