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
    field_args = dict(
        name = dict(
            render_kw = dict(
                class_ = 'scheduled-report',
            ),
        ),
        display_order = dict(
            render_kw = dict(
                class_ = 'scheduled-report',
                title =
                    'Scheduled report display order in editor table'
                    ' and new report prompt.',
            ),
        ),
        # TODO
        # - Get these automatically.
        show_lanes = dict(
            label = ScheduledReport.show_lanes.info['form_label'],
        ),
        show_chargeable_delays = dict(
            label = ScheduledReport.show_chargeable_delays.info['form_label'],
        ),
        show_delays_gt_30_count = dict(
            label = ScheduledReport.show_delays_gt_30_count.info['form_label'],
        ),
        show_on_time_performance_gt_15 = dict(
            label = ScheduledReport.show_on_time_performance_gt_15.info['form_label'],
        ),
        show_on_time_performance_gt_30 = dict(
            label = ScheduledReport.show_on_time_performance_gt_30.info['form_label'],
        ),
    ),
)
