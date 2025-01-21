from flask_wtf import FlaskForm
from wtforms import SubmitField

from performance.models import AssumedBest

from .base import BaseForm
from .fields import HiddenIntegerField
from .mixins import BackLinkMixin
from .mixins import SubmitMixin
from .model_converter import model_form

class AssumedBestBaseForm(
    BackLinkMixin,
    BaseForm,
    FlaskForm,
    SubmitMixin,
):
    class Meta:
        presentation = True

    # Define these so that model_form doesn't create visible fields.
    year = HiddenIntegerField()
    month = HiddenIntegerField()


AssumedBestForm = model_form(
    model = AssumedBest,
    base_class = AssumedBestBaseForm,
    exclude = (
        'created',
        'updated',
    ),
    field_args = {
        'lanes': {
            'label': 'Lanes',
        },
    },
)
