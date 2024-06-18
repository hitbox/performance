from flask import current_app
from wtforms import HiddenField

from ..models import Contract
from ..models import PerformanceTier
from ..models.contract import Operator

from .base import ModelForm
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin

class PerformanceTierForm(
    BackLinkMixin,
    ModelForm,
    SubmitUpdateDeleteMixin,
):
    """
    Arrival Performance tier for a performance range.
    """
    class Meta:
        model = PerformanceTier
        presentation = True
        only = [
            'tier',
            'performance_operator_start',
            'performance_range_start',
            'performance_operator_end',
            'performance_range_end',
        ]
        fields_order = only + ['submit', 'delete']
        field_args = dict(
            tier = dict(
                label = 'Tier',
            ),
            performance_range_start = dict(
                label = 'Range Start',
            ),
            performance_operator_start = dict(
                label = 'Start Operator',
                choices = Operator.as_choices(),
                default = Operator.GE,
            ),
            performance_range_end = dict(
                label = 'Range End',
            ),
            performance_operator_end = dict(
                label = 'End Operator',
                choices = Operator.as_choices(),
                default = Operator.LE,
            ),
        )

    contract_id = HiddenField()


class ContractForm(
    BackLinkMixin,
    ModelForm,
    SubmitUpdateDeleteMixin,
):
    """
    Arrival Performance Contract for a date range.
    """
    class Meta:
        model = Contract
        presentation = True
        only = [
            'name',
            'date_range_start',
            'date_range_end',
        ]
        fields_order = only + ['submit', 'delete']
        field_args = dict(
            name = dict(
                label = 'Name',
            ),
            date_range_start = dict(
                label = 'Start',
                render_kw = dict(
                    pattern = r'\d{4}-\d{2}-\d{2}'
                ),
            ),
            date_range_end = dict(
                label = 'End',
                render_kw = dict(
                    pattern = r'\d{4}-\d{2}-\d{2}'
                ),
            ),
        )

    def _update_for_app_config(self):
        use_date_range = current_app.config.get(
            'PERFORMANCE_CONTRACTS_USE_DATE_RANGE'
        )
        if not use_date_range:
            del self.date_range_start
            del self.date_range_end
