from wtforms import HiddenField

from ..models import Contract
from ..models import PerformanceTier

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
            'performance_range_start',
            'performance_range_end',
        ]
        fields_order = only + ['submit', 'delete']
        field_args = dict(
            tier = dict(
                label = 'Tier',
            ),
            performance_range_start = dict(
                label = 'Performance Range >',
            ),
            performance_range_end = dict(
                label = 'Performance Range <',
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
                    pattern = '\d{4}-\d{2}-\d{2}'
                ),
            ),
            date_range_end = dict(
                label = 'End',
                render_kw = dict(
                    pattern = '\d{4}-\d{2}-\d{2}'
                ),
            ),
        )

