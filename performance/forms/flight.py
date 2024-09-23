import sqlalchemy as sa
import wtforms.validators as wtforms_validators

from flask import request
from wtforms import HiddenField
from wtforms import StringField
from wtforms_alchemy import ClassMap
from wtforms_sqlalchemy.orm import ModelConverter
from wtforms_sqlalchemy.orm import converts
from wtforms_sqlalchemy.orm import model_form

from performance import models
from performance.extensions import db

from . import defaults
from .base import ModelForm
from .fields import StringTimeField
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin

DATE_FIELD_TITLE = 'Falls back to report date if blank.'
DATE_FIELD_TABINDEX = '-1'

def report_id_from_view_args():
    """
    Get the "current" report id from the view args.
    """
    return request.view_args['report_id']

def date_field_classes_string(*specific_classes):
    return ' '.join(('flight', 'date-entry') + specific_classes)

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
    'origin_delays_string': {
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
    'comment': {
        'label': 'Comment',
        'render_kw': {
            'class': 'flight',
            'cols': 100,
            'rows': 8,
        },
    },
}

class FlightModelConverter(ModelConverter):

    @converts('Time')
    def handle_time_types(self, column, field_args, **extra):
        return StringTimeField(**field_args)


class FlightFormBase(
    ModelForm,
    BackLinkMixin,
    SubmitUpdateDeleteMixin,
):
    class Meta:
        presentation = True

    report_id = HiddenField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dynamic_date_field_placeholder()
        self.flight_type_from_request()
        self.update_report_id_from_request()

    def dynamic_date_field_placeholder(self):
        """
        Dynamically add placeholder text to indicate what fallback date the
        estimated/actual difference in minutes, will use.
        """
        # NOTE: not sure whether to be general here, and go with
        #       .endswith('.create') and .endswith('.edit'). figure explicit is better.
        if request.endpoint == 'flight.create':
            report_id = report_id_from_view_args()
            report = models.Report.query.get(report_id)
            placeholder = report.date.isoformat()
        elif request.endpoint == 'flight.edit':
            flight_id = request.view_args['id']
            flight = models.Flight.query.get(flight_id)
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

    def flight_type_from_request(self):
        """
        Update the value of flight_type from the request.
        """
        if 'flight_type_id' in request.view_args:
            stmt = (
                sa.select(models.FlightType)
                .where(
                    models.FlightType.id == request.view_args['flight_type_id']
                )
            )
            self.flight_type.data = db.session.scalars(stmt).one()

    def update_report_id_from_request(self):
        if self.report_id.data is None:
            self.report_id.data = request.view_args['report_id']


FlightForm = model_form(
    model = models.Flight,
    db_session = db.session,
    base_class = FlightFormBase,
    exclude = [
        'report',
    ],
    field_args = field_args,
    converter = FlightModelConverter(),
)

FlightForm.flight_type = models.FlightType.as_query_select_field(
    validators = [
        wtforms_validators.DataRequired(),
    ],
)

FlightForm.origin_delays_string = StringField(
    'Delays',
    render_kw = dict(
        class_ = 'flight',
    )
)

FlightForm.destination_delays_string = StringField(
    'Delays',
    render_kw = dict(
        class_ = 'flight',
    )
)
