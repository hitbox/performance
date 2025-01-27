from flask_wtf import FlaskForm

from performance.models import Report

from .base import BaseForm
from .mixins import BackLinkMixin
from .mixins import SubmitMixin
from .model_converter import PerformanceModelConverter
from .model_converter import model_form
from .utils import remove_required_from_boolean_fields
from .utils import visibility_column_field_args
from .utils import visibility_column_names

# TODO
# - We surely do not need to specify field_args and only twice!

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


class ReportVisibilityFormBase(
    BackLinkMixin,
    BaseForm,
    FlaskForm,
    SubmitMixin,
):
    """
    Base class for the statistics visibility options for reports.
    """
    class Meta:
        model = Report


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


ReportVisibilityForm = model_form(
    model = Report,
    base_class = ReportVisibilityFormBase,
    only = visibility_column_names(),
    field_args = visibility_column_field_args(Report),
)

remove_required_from_boolean_fields(ReportVisibilityForm)
