from flask_wtf import FlaskForm

from performance.models import Contract

from .base import BaseForm
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin
from .model_converter import model_form
from .utils import remove_required_from_boolean_fields

class ContractBaseForm(
    BackLinkMixin,
    BaseForm,
    FlaskForm,
    SubmitUpdateDeleteMixin,
):
    """
    Performance Contract form base.
    """

    class Meta:
        fields_order = [
            'name',
            'date_range_start',
            'date_range_end',
            'submit',
            'delete',
        ]
        presentation = True


# Arrival Performance Contract for a date range.
ContractForm = model_form(
    model = Contract,
    base_class = ContractBaseForm,
    exclude = (
        'created',
        'updated',
        'tiers',
    ),
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
    ),
)

remove_required_from_boolean_fields(ContractForm)
