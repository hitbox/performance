from wtforms import SubmitField
from wtforms.validators import Optional
from wtforms.widgets import TextArea
from wtforms_sqlalchemy.orm import model_form

from performance.extensions import db
from performance.models import FlightType

from .base import ModelForm
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin
from .mixins import SubmitMixin

class BaseFlightType(
    BackLinkMixin,
    ModelForm,
    SubmitMixin,
):
    class Meta:
        model = FlightType


FlightTypeForm = model_form(
    model = FlightType,
    db_session = db.session,
    base_class = BaseFlightType,
    field_args = dict(
        is_controllable = dict(
            label = 'Is Controllable?',
            render_kw = dict(
                title = FlightType.is_controllable.doc,
            ),
        ),
        is_lane = dict(
            label = 'Is Lane?',
            render_kw = dict(
                title = FlightType.is_lane.doc,
            ),
        ),
        is_active = dict(
            label = 'Is Active?',
            render_kw = dict(
                title = FlightType.is_active.doc,
            ),
        ),
    )
)

# override the automatically added required validator (because column is
# nullable=false).
for fieldname in ['is_controllable', 'is_lane', 'is_active']:
    field = getattr(FlightTypeForm, fieldname)
    field.kwargs['validators'] = [Optional()]
