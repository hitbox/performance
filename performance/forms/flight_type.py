from wtforms import SubmitField
from wtforms.validators import Optional
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
            'is_lane',
        ]
        field_args = {
            'name': {
                'label': 'Name',
            },
            'report_order': {
                'label': 'Report Order',
            },
            # NOTE: These flag fields are set to Optional to avoid html
            #       required attribute.
            'is_controllable': {
                'label': 'Is Controllable?',
                'validators': [Optional()],
                'render_kw': {
                    'title': 'Flights in this category/type are considered for'
                             ' chargeable delays.',
                },
            },
            'is_lane': {
                'label': 'Is Lane?',
                'validators': [Optional()],
                'render_kw': {
                    'title': 'Flights in this category/type are counted'
                             ' as lanes.',
                },
            }
        }

    submit = SubmitField()
