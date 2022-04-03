import sqlalchemy as sa

from flask import request
from wtforms import HiddenField
from wtforms_alchemy import ClassMap
from wtforms_alchemy import QuerySelectField

from ..models import Flight
from ..models import FlightType
from ..models import Report
from ..types import DelayCodesType

from . import defaults
from .base import ModelForm
from .fields import DelayCodesField
from .fields import StringTimeField
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin

def report_id_from_view_args():
    """
    Get the "current" report id from the view args.
    """
    return request.view_args['report_id']

DATE_FIELD_TITLE = 'Falls back to report date if blank.'
DATE_FIELD_TABINDEX = '-1'

def date_field_classes_string(*specific_classes):
    return ' '.join(('flight', 'date-entry') + specific_classes)

class FlightForm(
    BackLinkMixin,
    ModelForm,
    SubmitUpdateDeleteMixin,
):
    class Meta:
        model = Flight
        type_map = ClassMap({
            sa.Time: StringTimeField,
            DelayCodesType: DelayCodesField,
        })
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
                    'class': date_field_classes_string('origin'),
                    'title': DATE_FIELD_TITLE,
                    'tabindex': DATE_FIELD_TABINDEX,
                },
            },
            'origin_departure_estimated_time': {
                'label': '',
                'render_kw': {
                    'class': 'flight origin time-entry',
                    'placeholder': 'ETD',
                },
            },
            'origin_departure_actual_date': {
                'label': 'ATD',
                'render_kw': {
                    'class': date_field_classes_string('origin'),
                    'title': DATE_FIELD_TITLE,
                    'tabindex': DATE_FIELD_TABINDEX,
                },
            },
            'origin_departure_actual_time': {
                'label': '',
                'render_kw': {
                    'class': 'flight origin time-entry',
                    'placeholder': 'ATD',
                },
            },
            'origin_delays': {
                'label': 'Delays',
                'render_kw': {
                    'autocomplete': 'off',
                    'class': 'flight delay',
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
                    'class': date_field_classes_string('destination'),
                    'title': DATE_FIELD_TITLE,
                    'tabindex': DATE_FIELD_TABINDEX,
                },
            },
            'destination_arrival_estimated_time': {
                'label': '',
                'render_kw': {
                    'class': 'flight origin time-entry',
                    'placeholder': 'ETA',
                },
            },
            'destination_arrival_actual_date': {
                'label': 'ATA',
                'render_kw': {
                    'class': date_field_classes_string('destination'),
                    'title': DATE_FIELD_TITLE,
                    'tabindex': DATE_FIELD_TABINDEX,
                },
            },
            'destination_arrival_actual_time': {
                'label': '',
                'render_kw': {
                    'class': 'flight destination time-entry',
                    'placeholder': 'ATA',
                },
            },
            'destination_delays': {
                'label': 'Delays',
                'render_kw': {
                    'autocomplete': 'off',
                    'class': 'flight delay',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dynamic_date_field_placeholder()

    def dynamic_date_field_placeholder(self):
        """
        Dynamically add placeholder text to indicate what fallback date the
        estimated/actual difference in minutes, will use.
        """
        # NOTE: not sure whether to be general here, and go with
        #       .endswith('.create') and .endswith('.edit'). figure explicit is better.
        if request.endpoint == 'flight.create':
            report_id = report_id_from_view_args()
            report = Report.query.get(report_id)
            placeholder = report.date.isoformat()
        elif request.endpoint == 'flight.edit':
            flight_id = request.view_args['id']
            flight = Flight.query.get(flight_id)
            placeholder = flight.report.date.isoformat()
        else:
            placeholder = 'date'

        attrnames = [
            'origin_departure_estimated_date',
            'origin_departure_actual_date',
            'destination_arrival_estimated_date',
            'destination_arrival_actual_date',
        ]

        for attrname in attrnames:
            field = getattr(self, attrname)
            field.render_kw['placeholder'] = placeholder
