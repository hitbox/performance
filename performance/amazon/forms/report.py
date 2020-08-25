from wtforms.widgets.html5 import NumberInput

from ...forms.base import ModelForm
from ...forms.mixins import BackLinkMixin
from ...forms.mixins import SubmitUpdateDeleteMixin

from ..models import Report

class ReportForm(
    BackLinkMixin,
    ModelForm,
    SubmitUpdateDeleteMixin,
):
    class Meta:
        model = Report
        only = [
            'previous_days_performance_percent',
            'previous_days_performance_lanes',
            'previous_days_performance_late',
            'arrival_performance_mtd_percent',
            'arrival_performance_mtd_lanes',
            'arrival_performance_mtd_late',
            'arrival_performance_mtd_30_percent',
            'arrival_performance_mtd_30_lanes',
            'arrival_performance_mtd_30_late',
            'days_at_100_percent',
            'assumed_best_arrival_performance_for_month_percent',
            'qtd_performance_percent',
            'qtd_performance_lanes',
            'qtd_performance_late',
            'system_detail',
        ]
        field_args = {
            key: {
                'render_kw': {
                    'class': 'narrowest'
                }
            }
            for key in only
        }

        field_args['system_detail']['render_kw']['cols'] = 120
        field_args['system_detail']['render_kw']['rows'] = 15

        _percent_fields = ['previous_days_performance_percent',
                           'arrival_performance_mtd_percent',
                           'arrival_performance_mtd_30_percent',
                           'qtd_performance_percent',
                           'assumed_best_arrival_performance_for_month_percent']
        for key, options in field_args.items():
            if key in _percent_fields:
                options['render_kw']['class'] += ' percent'
