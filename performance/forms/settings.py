from flask_wtf import FlaskForm

from performance.models import FlightType
from performance.models import Performance

from .base import BaseForm
from .mixins import BackLinkMixin
from .mixins import SubmitMixin
from .model_converter import model_form

class BaseSettingsForm(
    BaseForm,
    FlaskForm,
    SubmitMixin,
):
    class Meta:
        presentation = True


SettingsForm = model_form(
    model = Performance,
    type_name = 'SettingsForm',
    base_class = BaseSettingsForm,
    field_args = dict(
        default_flight_type = dict(
            get_label = 'name',
            render_kw = dict(
                title = Performance.default_flight_type_id.doc,
            ),
        ),
    ),
)

# NOTES
# model_form detects a "direction" attribute and overwrites the query_factory,
# so we overwrite the UnboundField kwargs that it makes to get the ordering we
# want.

SettingsForm.default_flight_type.kwargs['query_factory'] = FlightType.query_factory
