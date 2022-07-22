from wtforms import SubmitField

from ..models import Delay

from .base import ModelForm
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin

class DelayForm(
    BackLinkMixin,
    ModelForm,
):
    """
    Delay object form.
    """
    class Meta:
        model = Delay
        presentation = True
        field_args = {
            'code': {
                'label': 'Code',
            },
            'is_controllable': {
                'label': 'Controllable?',
            },
            'is_cancelled_lane': {
                'label': 'Always Lane?',
            },
            'is_always_show': {
                'label': 'Always Show?',
            },
        }
        fields_order = [
            'code',
            'is_controllable',
            'is_cancelled_lane',
            'is_always_show',
            'submit',
            'delete',
        ]

    submit = SubmitField()
