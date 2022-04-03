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

# FIXME: form instantiation hits the database.

def report_id_from_view_args():
    return request.view_args['report_id']

def get_placeholder_date_string():
    """
    Show the flight's report date as the placeholder of the optional
    estimated/actual origin/destination date fields. This is the date used when
    these fields are left empty.
    """
    if request.endpoint == 'flight.create':
        report_id = request.view_args['report_id']
        report = Report.query.get(report_id)
        date = report.date
    elif request.endpoint == 'flight.edit':
        flight_id = request.view_args['id']
        flight = Flight.query.get(flight_id)
        date = flight.report.date
    else:
        return 'date'
    fmt = current_app.config['DATEFMT']
    string = date.strftime(fmt)
    return string

def date_field_render_kw(*classes, **extra):
    """
    Return the render_kw dict for the date fields.
    """
    classes = set(classes)
    for cls in ['flight', 'date-entry']:
        if cls not in classes:
            classes.add(cls)

    placeholder_date_string = get_placeholder_date_string()
    render_kw = {
        'class': ' '.join(classes),
        'placeholder': placeholder_date_string,
        'tabindex': '-1',
        'title': 'Falls back to report date if blank.',
    }
    return render_kw

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
                'render_kw': date_field_render_kw('origin'),
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
                'render_kw': date_field_render_kw('origin'),
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
                'render_kw': date_field_render_kw('destination'),
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
                'render_kw': date_field_render_kw('destination'),
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
