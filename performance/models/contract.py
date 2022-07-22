from performance.extensions import db

from .mixin import AppContextMixin
from .mixin import MetaMixin

class Contract(
    AppContextMixin,
    MetaMixin,
    db.Model,
):
    """
    Performance contract applied to a date range.
    """

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String,
        nullable = False,
        doc = 'Friendly name for contract.',
    )

    date_range_start = db.Column(db.Date)

    date_range_end = db.Column(db.Date)

    tiers = db.relationship(
        'PerformanceTier',
        back_populates = 'contract',
        order_by = 'PerformanceTier.tier',
    )


class PerformanceTier(
    AppContextMixin,
    MetaMixin,
    db.Model,
):
    """
    A range of performance corresponding to a tier number.
    """

    id = db.Column(db.Integer, primary_key=True)

    tier = db.Column(db.Integer, nullable=False)

    performance_range_start = db.Column(db.Numeric)

    performance_range_end = db.Column(db.Numeric)

    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'))
    contract = db.relationship('Contract', back_populates='tiers')

    def human_performance_range(self):
        """
        Return human readable performance range string.
        """
        parts = [
            self.performance_range_start,
            self.performance_range_end,
        ]
        parts = [f'{opstr}{part:.1f}%' for part, opstr in zip(parts, '><') if part]
        return ' and '.join(parts)
