import sqlalchemy as sa

from wtforms import HiddenField
from wtforms.validators import DataRequired
from wtforms_alchemy import ClassMap

from .. import queries
from ..models import ScheduledFlight

from .base import ModelForm
from .fields import StringTimeField
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin

_class_names = 'scheduled-flight'

class ScheduledFlightForm(
    BackLinkMixin,
    ModelForm,
    SubmitUpdateDeleteMixin,
):
    class Meta:
        model = ScheduledFlight
        presentation = True
        type_map = ClassMap({
            sa.Time: StringTimeField,
        })
        only = [
            'flight_number',
            'origin_station',
            'origin_departure_estimated_time',
            'destination_station',
            'destination_arrival_estimated_time',
        ]
        fields_order = ['flight_type'] + only + ['submit', 'delete']
        # overriding estimated times labels because there's no date fields
        field_args = {
            'flight_number': {
                'render_kw': {
                    'class': f'{_class_names}',
                    'placeholder': 'Flight Number',
                },
            },
            'origin_station': {
                'label': 'Orig.',
                'render_kw': {
                    'class': f'{_class_names}',
                    'placeholder': 'Origin Station',
                },
            },
            'destination_station': {
                'label': 'Dest.',
                'render_kw': {
                    'class': f'{_class_names}',
                    'placeholder': 'Destination Station',
                },
            },
            'origin_departure_estimated_time': {
                'label': 'ETD',
                'render_kw': {
                    'class': f'{_class_names} origin',
                    'placeholder': 'ETD',
                },
            },
            'destination_arrival_estimated_time': {
                'label': 'ETA',
                'render_kw': {
                    'class': f'{_class_names} origin',
                    'placeholder': 'ETA',
                },
            },
        }

    scheduled_report_id = HiddenField(validators=[DataRequired()])

    flight_type_id = HiddenField(
        default = lambda: queries.get_scheduled_flight_type_instance().id,
        filters = [int],
    )
