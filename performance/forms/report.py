from flask_wtf import FlaskForm

from performance.models import Report

from .base import BaseForm
from .mixins import BackLinkMixin
from .mixins import SubmitMixin
from .model_converter import PerformanceModelConverter
from .model_converter import model_form

class ReportFormBase(
    BackLinkMixin,
    BaseForm,
    FlaskForm,
    SubmitMixin,
):
    class Meta:
        model = Report
        only = [
            'system_detail',
        ]
        field_args = {
            'system_detail': {
                'render_kw': {
                    'cols': 133,
                    'rows': 15,
                },
            },
        }


# Form to edit the "system detail" field of a report.
ReportForm = model_form(
    model = Report,
    base_class = ReportFormBase,
    only = [
        'system_detail',
    ],
    field_args = dict(
        system_detail = dict(
            render_kw = dict(
                cols = 133,
                rows = 15,
            ),
        ),
    ),
    converter = PerformanceModelConverter(),
)
