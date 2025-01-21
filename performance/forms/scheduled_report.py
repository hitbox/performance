from flask_wtf import FlaskForm

from performance.models import ScheduledReport

from .base import BaseForm
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin
from .model_converter import model_form

class BaseForm(
    BackLinkMixin,
    BaseForm,
    FlaskForm,
    SubmitUpdateDeleteMixin,
):
    class Meta:
        fields_order = [
            'submit',
            'delete',
        ]
        presentation = True


ScheduledReportForm = model_form(
    model = ScheduledReport,
    base_class = BaseForm,
    exclude = (
        'scheduled_flights',
        'created',
        'updated',
    ),
    field_args = {
        'name': {
            'render_kw': {'class': 'scheduled-report'},
        },
        'display_order': {
            'render_kw': {
                'class': 'scheduled-report',
                'title':
                    'Scheduled report display order in editor table'
                    ' and new report prompt.',
            },
        },
    },
)
