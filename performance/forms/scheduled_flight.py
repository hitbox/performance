from datetime import date

from flask_wtf import FlaskForm
from wtforms import validators as wtforms_validators
from wtforms.validators import ValidationError

from performance import settings
from performance.models import FlightType
from performance.models import ScheduledFlight

from .base import BaseForm
from .fields import HiddenIntegerField
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin
from .model_converter import model_form

class DateFormatString:
    """
    Validate date format string resolves to a date.
    """

    def __call__(self, form, field):
        if not field.data:
            return

        context = ScheduledFlight.context_for_dates(date.today())

        format_string = field.data

        try:
            value = ScheduledFlight.resolve_date(None, format_string, **context)
        except ValueError:
            raise ValidationError(f'Format string does not resolve to a date.')
        

_only = [
    'flight_number',
    'origin_station',
    'origin_departure_estimated_date_template',
    'origin_departure_estimated_time',
    'destination_station',
    'destination_arrival_estimated_date_template',
    'destination_arrival_estimated_time',
    'is_active',
    'flight_type',
]

class BaseScheduledFlightForm(
    BackLinkMixin,
    BaseForm,
    FlaskForm,
    SubmitUpdateDeleteMixin,
):
    """
    Mix useful things together for base.
    """
    class Meta:
        fields_order = ['flight_type'] + _only + ['submit', 'delete']
        presentation = True

    scheduled_report_id = HiddenIntegerField()


_class_names = 'scheduled-flight'

_field_args = dict(
    flight_type = dict(
        get_label = 'name',
        default = settings.default_flight_type,
    ),
    flight_number = dict(
        render_kw = dict(
            placeholder = 'Flight Number',
        ),
    ),
    origin_station = dict(
        label = 'Orig.',
        render_kw = dict(
            placeholder = 'Origin Station',
        ),
    ),
    destination_station = dict(
        label = 'Dest.',
        render_kw = dict(
            placeholder = 'Destination Station',
        ),
    ),
    origin_departure_estimated_date_template = {
        'label': 'ETD',
        'validators': [
            DateFormatString(),
        ],
        'render_kw': {
            'class_': _class_names + ' origin data',
            'placeholder': 'Date',
        },
    },
    origin_departure_estimated_time = dict(
        label = 'ETD',
        render_kw = dict(
            class_ = _class_names + ' origin',
            placeholder = 'ETD',
        ),
    ),
    destination_arrival_estimated_date_template = {
        'label': 'ETA',
        'validators': [
            DateFormatString(),
        ],
        'render_kw': {
            'class_': _class_names + ' origin data',
            'placeholder': 'Date',
        },
    },
    destination_arrival_estimated_time = dict(
        label = 'ETA',
        render_kw = dict(
            class_ = _class_names + ' origin',
            placeholder = 'ETA',
        ),
    ),
    is_active = dict(
        label = 'Active?',
        render_kw = dict(
            title = ScheduledFlight.is_active.doc,
        ),
    ),
)

ScheduledFlightForm = model_form(
    model = ScheduledFlight,
    base_class = BaseScheduledFlightForm,
    only = _only,
    field_args = _field_args,
)

fieldnames = [
    'flight_number',
    'origin_station',
    'destination_station',
    'origin_departure_estimated_time',
    'destination_arrival_estimated_time',
]
for fieldname in fieldnames:
    field = getattr(ScheduledFlightForm, fieldname)
    field.kwargs.setdefault('render_kw', dict())
    field.kwargs['render_kw'].setdefault('class_', _class_names)

ScheduledFlightForm.is_active.kwargs['validators'] = [wtforms_validators.Optional()]

# Setting this in the base mix above, makes all the attributes come through as fields.
ScheduledFlightForm.Meta.model = ScheduledFlight

ScheduledFlightForm.flight_type.kwargs['query_factory'] = FlightType.query_factory
