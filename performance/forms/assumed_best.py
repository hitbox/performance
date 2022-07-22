from wtforms import SubmitField

from .base import ModelForm
from .mixins import BackLinkMixin
from .mixins import SubmitMixin

from ..models import AssumedBest

class AssumedBestForm(
    BackLinkMixin,
    ModelForm,
):
    class Meta:
        model = AssumedBest
        only = ['lanes']

    submit = SubmitField('Update')
