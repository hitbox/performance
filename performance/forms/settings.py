from wtforms_sqlalchemy.orm import model_form

from performance.extensions import db
from performance.models import FlightType
from performance.models import Performance

from .base import ModelForm

SettingsForm = model_form(
    model = Performance,
    db_session = db.session,
    base_class = ModelForm,
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
