from wtforms_sqlalchemy.orm import model_form

from performance.extensions import db
from performance.models import Report

from .base import ModelForm
from .mixins import BackLinkMixin
from .mixins import SubmitMixin
from .model_converter import PerformanceModelConverter

class ReportForm(
    BackLinkMixin,
    ModelForm,
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


class ReportFormBase(BackLinkMixin, ModelForm, SubmitMixin):
    pass


ReportForm = model_form(
    model = Report,
    db_session = db.session,
    base_class = ReportFormBase,
    only = ['system_detail'],
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
