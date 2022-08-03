from wtforms import SubmitField

from .base import ModelForm
from .fields import HiddenIntegerField
from .mixins import BackLinkMixin

from ..models import AssumedBest

class AssumedBestForm(
    BackLinkMixin,
    ModelForm,
):
    class Meta:
        model = AssumedBest
        only = [
            'year',
            'month',
            'lanes',
        ]
        field_args = {
            'lanes': {
                'label': 'Lanes',
            },
        }
        presentation = True

    year = HiddenIntegerField()
    month = HiddenIntegerField()

    submit = SubmitField('Update')
