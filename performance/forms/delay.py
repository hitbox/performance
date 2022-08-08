from wtforms import SubmitField
from wtforms.widgets import TextArea

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
        only = [
            'code',
            'description',
            'is_controllable',
        ]
        field_args = {
            'code': {
                'label': 'Code',
            },
            'description': {
                'label': 'Description',
                'widget': TextArea(),
                'render_kw': {
                    'cols': 40,
                    'rows': 5,
                }
            },
            'is_controllable': {
                'label': 'Controllable?',
            },
        }
        fields_order = [
            'code',
            'description',
            'is_controllable',
            'submit',
            'delete',
        ]

    submit = SubmitField()
