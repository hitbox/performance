from performance.forms.base import ModelForm
from performance.forms.mixins import BackLinkMixin
from performance.forms.mixins import SubmitUpdateDeleteMixin

from ..models import Report

class ReportForm(
    BackLinkMixin,
    ModelForm,
    SubmitUpdateDeleteMixin,
):
    class Meta:
        model = Report
        only = [
            'aircraft_spares_1200',
            'aircraft_spares_2000',
            'aircraft_spares_0300',
            'crew_info_1200',
            'crew_info_2000',
            'crew_info_0300',
            'abx_amazon_arrival_performance_mtd_lanes',
            'abx_amazon_arrival_performance_mtd_late',
            'abx_amazon_arrival_performance_mtd_percent',
            'abx_amazon_days_at_100_percent',
            'abx_amazon_previous_days_performance_lanes',
            'abx_amazon_previous_days_performance_late',
            'abx_amazon_previous_days_performance_percent',
            'abx_amazon_qtd_performance_lanes',
            'abx_amazon_qtd_performance_late',
            'abx_amazon_qtd_performance_percent',
            'charter_detail',
            'dhl_arrival_performance_mtd',
            'dhl_arrival_performance_mtd_30_lanes',
            'dhl_arrival_performance_mtd_30_late',
            'dhl_arrival_performance_mtd_30_percent',
            'dhl_arrival_performance_mtd_lanes',
            'dhl_arrival_performance_mtd_late',
            'dhl_arrival_performance_wtd',
            'dhl_arrival_performance_wtd_lanes',
            'dhl_arrival_performance_wtd_late',
            'dhl_assumed_best_arrival_performance_for_month_lanes',
            'dhl_assumed_best_arrival_performance_for_month_late',
            'dhl_assumed_best_arrival_performance_for_month_percent',
            'dhl_days_at_100_percent',
            'dhl_previous_overall_performance',
            'dhl_previous_overall_performance_lanes',
            'dhl_previous_overall_performance_late',
            'dhl_qtd_performance',
            'dhl_qtd_performance_lanes',
            'dhl_qtd_performance_late',
            'dhl_todays_arrival_performance_front_half',
            'dhl_todays_arrival_performance_front_half_lanes',
            'dhl_todays_arrival_performance_front_half_late',
            'extra_section_detail',
            'ferry_flight_detail',
            'system_detail',
        ]

        # add class to all fields
        field_args = {
            key: {
                'render_kw': {
                    'class': 'narrowest'
                }
            }
            for key in only
        }

        # add render_kw cols/rows to textarea fields
        fields = [
            'charter_detail',
            'extra_section_detail',
            'ferry_flight_detail',
            'system_detail',
        ]
        for field in fields:
            field_args[field]['render_kw']['cols'] = 120
            field_args[field]['render_kw']['rows'] = 15

        # add render_kw class to percent fields
        _percent_fields = [
            'dhl_arrival_performance_mtd',
            'dhl_arrival_performance_mtd_30_percent',
            'dhl_arrival_performance_wtd',
            'dhl_assumed_best_arrival_performance_for_month_percent',
            'dhl_previous_overall_performance',
            'dhl_qtd_performance',
            'dhl_todays_arrival_performance_front_half',
            'abx_amazon_arrival_performance_mtd_percent',
            'abx_amazon_previous_days_performance_percent',
            'abx_amazon_qtd_performance_percent',
        ]
        for key, options in field_args.items():
            if key in _percent_fields:
                options['render_kw']['class'] += ' percent'
