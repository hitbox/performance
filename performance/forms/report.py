from performance.forms.base import ModelForm
from performance.forms.mixins import BackLinkMixin
from performance.forms.mixins import SubmitMixin

from ..models import Report

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
