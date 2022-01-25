import sqlalchemy as sa

from wtforms import HiddenField
from wtforms_alchemy import ClassMap
from wtforms_alchemy import QuerySelectField

from ..models import FlightType
from ..models import ScheduledFlight

from . import defaults
from .base import ModelForm
from .fields import StringTimeField
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin

class ScheduledFlightForm(
    BackLinkMixin,
    ModelForm,
    SubmitUpdateDeleteMixin,
):
    class Meta:
        model = ScheduledFlight
        type_map = ClassMap({sa.Time: StringTimeField})
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
                    'class': 'flight',
                },
            },
            'origin_station': {
                'label': 'Orig.',
                'render_kw': {
                    'class': 'flight',
                },
            },
            'destination_station': {
                'label': 'Dest.',
                'render_kw': {
                    'class': 'flight',
                },
            },
            'origin_departure_estimated_time': {
                'label': 'ETD',
                'render_kw': {
                    'class': 'flight origin',
                    'placeholder': 'ETD',
                },
            },
            'destination_arrival_estimated_time': {
                'label': 'ETA',
                'render_kw': {
                    'class': 'flight origin',
                    'placeholder': 'ETA',
                },
            },
        }

    scheduled_report_id = HiddenField()

    flight_type = QuerySelectField(
        'Type',
        default = defaults.flight_type,
        get_label = 'name',
        query_factory = lambda: FlightType.query.order_by(FlightType.report_order).all(),
        render_kw = {
            'class': 'flight',
        },
    )
