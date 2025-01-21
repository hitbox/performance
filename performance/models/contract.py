from enum import Enum

from sqlalchemy_utils import ChoiceType

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

    # Metadata mainly for user interfaces.
    __notes__ = {
        'admin_note':
            'Performance contracts define a name and date range for a set'
            ' of performance tiers to apply.',
    }

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


class Operator(Enum):
    """
    Comparison operators
    """
    LT = 1
    LE = 2
    EQ = 3
    GE = 4
    GT = 5

    @classmethod
    def as_choices(cls):
        get_label = '{0.char} ({0.text})'.format
        return [(member.value, get_label(member)) for member in cls]


Operator.LT.char = '<'
Operator.LT.text = 'less than'

Operator.LE.char = '≤'
Operator.LE.text = 'less than or equal'

Operator.EQ.char = '='
Operator.EQ.text = 'equal'

Operator.GE.char = '≥'
Operator.GE.text = 'greater than or equal'

Operator.GT.char = '>'
Operator.GT.text = 'greater than'

_valid_operator_values = tuple(op.value for op in Operator)

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

    performance_operator_start = db.Column(
        ChoiceType(
            Operator,
            impl = db.Integer(),
        ),
        db.CheckConstraint(
            f'performance_operator_start IN {_valid_operator_values}'
        ),
        default = Operator.GT,
        server_default = str(Operator.GT.value),
        nullable = False,
    )

    performance_range_end = db.Column(db.Numeric)

    performance_operator_end = db.Column(
        ChoiceType(
            Operator,
            impl = db.Integer(),
        ),
        db.CheckConstraint(
            f'performance_operator_end IN {_valid_operator_values}'
        ),
        default = Operator.LT,
        server_default = str(Operator.LT.value),
        nullable = False,
    )

    contract_id = db.Column(db.Integer, db.ForeignKey('contract.id'))
    contract = db.relationship('Contract', back_populates='tiers')

    def human_performance_range(self):
        """
        Return human readable performance range string.
        """
        parts = [
            (self.performance_range_start, self.performance_operator_start),
            (self.performance_range_end, self.performance_operator_end),
        ]
        parts = [f'{op.char}{value:.1f}%' for value, op in parts if value]
        return ' and '.join(parts)
