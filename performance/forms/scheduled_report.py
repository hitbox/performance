from ..models import ScheduledReport

from .base import ModelForm
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin

class ScheduledReportForm(
    BackLinkMixin,
    ModelForm,
    SubmitUpdateDeleteMixin,
):
    class Meta:
        model = ScheduledReport
        presentation = True
        only = [
            'name',
            'display_order',
        ]
        fields_order = only + ['submit', 'delete']
        field_args = {
            'name': {
                'label': 'Name',
                'render_kw': {'class': 'scheduled-report'},
            },
            'display_order': {
                'label': 'Display Order',
                'render_kw': {'class': 'scheduled-report'},
            },
        }
