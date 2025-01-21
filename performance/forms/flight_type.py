from flask_wtf import FlaskForm

from performance.models import FlightType

from .base import BaseForm
from .mixins import BackLinkMixin
from .mixins import SubmitMixin
from .model_converter import model_form
from .utils import remove_required_from_boolean_fields

class BaseFlightType(
    BackLinkMixin,
    BaseForm,
    FlaskForm,
    SubmitMixin,
):
    """
    Base FlightType Form.
    """


FlightTypeForm = model_form(
    model = FlightType,
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

remove_required_from_boolean_fields(FlightTypeForm)
