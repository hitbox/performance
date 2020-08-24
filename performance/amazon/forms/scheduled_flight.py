import sqlalchemy as sa

from flask import request
from wtforms import HiddenField
from wtforms_alchemy import ClassMap
from wtforms_alchemy import QuerySelectField

from ...forms import defaults
from ...forms.base import ModelForm
from ...forms.fields import StringTimeField
from ...forms.mixins import BackLinkMixin
from ...forms.mixins import SubmitUpdateDeleteMixin
from ...models import FlightType

from ..models import ScheduledFlight

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
            'origin_departure_estimated_time': {
                'label': 'ETD',
            },
            'destination_arrival_estimated_time': {
                'label': 'ETA',
            },
        }

    scheduled_report_id = HiddenField()

    flight_type = QuerySelectField(
        'Flight Type',
        default = defaults.flight_type,
        get_label = 'name',
        query_factory = lambda: FlightType.query.order_by(FlightType.order).all()
    )
