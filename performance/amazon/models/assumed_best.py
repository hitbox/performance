from datetime import time
from operator import attrgetter

import sqlalchemy as sa

from performance.extensions import db
from performance.models.mixin import MetaMixin

class AssumedBest(MetaMixin, db.Model):
    """
    Assumed best performance number for a month.
    """

    id = db.Column(db.Integer, primary_key=True)

    month = db.Column(db.Integer)
    year = db.Column(db.Integer)

    lanes = db.Column(db.Integer, info=dict(label='Lanes'))
