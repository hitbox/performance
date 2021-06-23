from performance.extensions import db
from performance.models.mixin import MetaMixin

class PerformanceMeta(MetaMixin, db.Model):
    """
    Extra performance data.
    """

    id = db.Column(db.Integer, primary_key=True)

    assumed_best_lanes_quarter = db.Column(db.Integer)
