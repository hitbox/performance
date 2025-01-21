from flask_wtf import FlaskForm
from wtforms.widgets import TextArea

from performance.models import Delay

from .base import BaseForm
from .mixins import BackLinkMixin
from .mixins import SubmitMixin
from .model_converter import model_form
from .utils import remove_required_from_boolean_fields

class BaseDelayForm(
    BackLinkMixin,
    BaseForm,
    FlaskForm,
    SubmitMixin,
):

    class Meta:
        presentation = True
        fields_order = [
            'code',
            'is_controllable',
            'is_cancelled_lane',
            'is_always_show',
            'description',
            'submit',
            'delete',
        ]


field_args = {
    'code': {
        'label': 'Code',
    },
    'is_controllable': {
        'label': 'Controllable?',
    },
    'is_cancelled_lane': {
        'label': 'Cancelled Lane?',
    },
    'is_always_show': {
        'label': 'Always Show?',
    },
    'description': {
        'label': 'Description',
        'widget': TextArea(),
        'render_kw': {
            'cols': 40,
            'rows': 5,
        }
    },
}

DelayForm = model_form(
    model = Delay,
    base_class = BaseDelayForm,
    field_args = field_args,
    exclude = (
        'as_origin_delay',
        'as_destination_delay',
    ),
)

remove_required_from_boolean_fields(DelayForm)
