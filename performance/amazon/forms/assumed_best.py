from wtforms import SubmitField

from performance.forms.base import ModelForm
from performance.forms.mixins import BackLinkMixin
from performance.forms.mixins import SubmitMixin

from ..models import AssumedBest

class AssumedBestForm(
    BackLinkMixin,
    ModelForm,
):
    class Meta:
        model = AssumedBest
        only = ['lanes']

    submit = SubmitField('Update')
