import sqlalchemy as sa

from flask import request
from wtforms import HiddenField
from wtforms import SelectField
from wtforms_alchemy import ClassMap
from wtforms_alchemy import QuerySelectField

from performance.forms import defaults
from performance.forms.base import ModelForm
from performance.forms.fields import StringTimeField
from performance.forms.mixins import BackLinkMixin
from performance.forms.mixins import SubmitUpdateDeleteMixin
from performance.models import FlightType

from performance.dhl.models import Bound
from performance.dhl.models import Flight

def report_id_from_view_args():
    return request.view_args['report_id']

class FlightForm(
    BackLinkMixin,
    ModelForm,
    SubmitUpdateDeleteMixin,
):
    class Meta:
        model = Flight
        type_map = ClassMap({sa.Time: StringTimeField})
        only = [
            'leg',
            'flight_number',
            'tail_number',
            'weight',
            'origin_station',
            'origin_departure_estimated_date',
            'origin_departure_estimated_time',
            'origin_departure_actual_date',
            'origin_departure_actual_time',
            'origin_delays',
            'destination_station',
            'destination_arrival_estimated_date',
            'destination_arrival_estimated_time',
            'destination_arrival_actual_date',
            'destination_arrival_actual_time',
            'destination_delays',
            'comment',
        ]
        fields_order = [
            'bound',
            'flight_type',
            'leg',
            'flight_number',
            'tail_number',
            'weight',
            'origin_station',
            'origin_departure_estimated_date',
            'origin_departure_estimated_time',
            'origin_departure_actual_date',
            'origin_departure_actual_time',
            'origin_delays',
            'destination_station',
            'destination_arrival_estimated_date',
            'destination_arrival_estimated_time',
            'destination_arrival_actual_date',
            'destination_arrival_actual_time',
            'destination_delays',
            'comment',
            'submit',
            'delete',
        ]
        field_args = {
            'flight_number': {
                'label': 'Flight',
                'render_kw': {
                    'class': 'flight narrowest',
                },
            },
            'leg': {
                'label': 'Leg',
                'render_kw': {
                    'class': 'flight narrowest',
                },
            },
            'tail_number': {
                'label': 'Tail',
                'render_kw': {
                    'class': 'flight narrowest',
                },
            },
            'weight': {
                'label': 'Weight',
                'render_kw': {
                    'class': 'flight narrowest',
                },
            },
            'origin_station': {
                'label': 'Station',
                'render_kw': {
                    'class': 'flight narrowest',
                },
            },
            'origin_departure_estimated_date': {
                'label': 'ETD',
                'render_kw': {
                    'class': 'flight date-entry',
                    'placeholder': 'optional date',
                    'tabindex': '-1',
                },
            },
            'origin_departure_estimated_time': {
                'label': '',
                'render_kw': {
                    'class': 'flight time-entry',
                    'placeholder': 'ETD',
                },
            },
            'origin_departure_actual_date': {
                'label': 'ATD',
                'render_kw': {
                    'placeholder': 'optional date',
                    'class': 'flight date-entry',
                    'tabindex': '-1',
                },
            },
            'origin_departure_actual_time': {
                'label': '',
                'render_kw': {
                    'class': 'flight time-entry',
                    'placeholder': 'ATD',
                },
            },
            'origin_delays': {
                'label': 'Delays',
                'render_kw': {
                    'autocomplete': 'off',
                    'class': 'flight',
                    'style': 'width: 45rem',
                },
            },
            'destination_station': {
                'label': 'Station',
                'render_kw': {
                    'class': 'flight narrowest',
                },
            },
            'destination_arrival_estimated_date': {
                'label': 'ETA',
                'render_kw': {
                    'placeholder': 'optional date',
                    'class': 'flight date-entry',
                    'tabindex': '-1',
                },
            },
            'destination_arrival_estimated_time': {
                'label': '',
                'render_kw': {
                    'class': 'flight time-entry',
                    'placeholder': 'ETA',
                },
            },
            'destination_arrival_actual_date': {
                'label': 'ATA',
                'render_kw': {
                    'placeholder': 'optional date',
                    'class': 'flight date-entry',
                    'tabindex': '-1',
                },
            },
            'destination_arrival_actual_time': {
                'label': '',
                'render_kw': {
                    'class': 'flight time-entry',
                    'placeholder': 'ATA',
                },
            },
            'destination_delays': {
                'label': 'Delays',
                'render_kw': {
                    'autocomplete': 'off',
                    'class': 'flight',
                    'style': 'width: 45rem',
                },
            },
            'comment': {
                'label': 'Comment',
                'render_kw': {
                    'class': 'flight',
                    'cols': 100,
                    'rows': 8,
                },
            },
        }

    report_id = HiddenField(default=report_id_from_view_args)

    bound = QuerySelectField(
        'Bound',
        get_label = 'name',
        query_factory = lambda: Bound.query.order_by(Bound.report_order).all(),
        render_kw = {
            'class': 'narrower flight',
            'autofocus': True,
        }
    )
    flight_type = QuerySelectField(
        'Flight Type',
        default = defaults.flight_type,
        get_label = 'name',
        query_factory = lambda: FlightType.query.order_by(FlightType.report_order).all(),
        render_kw = {
            'class': 'narrower flight',
            'autofocus': True,
        }
    )
