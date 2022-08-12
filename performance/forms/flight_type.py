from wtforms import SubmitField
from wtforms.widgets import TextArea

from ..models import FlightType

from .base import ModelForm
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin

class FlightTypeForm(
    BackLinkMixin,
    ModelForm,
):
    """
    FlightType object form.
    """
    class Meta:
        model = FlightType
        presentation = True
        only = [
            'name',
            'report_order',
            'is_controllable',
        ]
        field_args = {
            'name': {
                'label': 'Name',
            },
            'report_order': {
                'label': 'Report Order',
            },
            'is_controllable': {
                'label': 'Is Controllable?',
            }
        }

    submit = SubmitField()
