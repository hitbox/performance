from flask_wtf import FlaskForm
from wtforms import HiddenField

from performance.models import PerformanceTier
from performance.models.contract import Operator

from .base import BaseForm
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin
from .model_converter import model_form
from .utils import remove_required_from_boolean_fields

class PerformanceTierBaseForm(
    BackLinkMixin,
    BaseForm,
    FlaskForm,
    SubmitUpdateDeleteMixin,
):
    """
    Base for Contract and PerformanceTier forms.
    """

    class Meta:
        presentation = True

    contract_id = HiddenField()


# Arrival Performance tier form for a performance range.
PerformanceTierForm = model_form(
    model = PerformanceTier,
    base_class = PerformanceTierBaseForm,
    exclude = (
        'contract',
        'created',
        'tiers',
        'updated',
    ),
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
    ),
)

remove_required_from_boolean_fields(PerformanceTierForm)
