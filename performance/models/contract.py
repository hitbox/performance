from performance.extensions import db
from performance.models.mixin import MetaMixin

class Contract(MetaMixin, db.Model):
    """
    Performance contract applied to a date range.
    """

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String,
        doc = 'Friendly name for contract.',
        info = dict(
            label = 'Name',
        ),
    )

    date_range_start = db.Column(
        db.Date,
        info = dict(
            label = 'Start',
        ),
    )
    date_range_end = db.Column(
        db.Date,
        info = dict(
            label = 'End',
        ),
    )

    tiers = db.relationship(
        'PerformanceTier',
        back_populates = 'contract',
        order_by = 'PerformanceTier.order',
    )


class PerformanceTier(MetaMixin, db.Model):
    """
    A range of performance corresponding to a tier number.
    """

    id = db.Column(db.Integer, primary_key=True)

    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'))
    contract = db.relationship('Contract', back_populates='tiers')

    order = db.Column(
        db.Integer,
        doc = 'Ordering for this record.',
        info = dict(
            label = 'Display Order',
        ),
    )

    tier = db.Column(
        db.Integer,
        info = dict(
            label = 'Annual Cost Escalation Tier',
        ),
    )

    performance_range_start = db.Column(
        db.Numeric,
        info = dict(
            label = 'Performance Range >',
        ),
    )

    performance_range_end = db.Column(
        db.Numeric,
        info = dict(
            label = 'Performance Range <',
        ),
    )

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
