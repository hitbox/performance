from performance.forms.base import ModelForm
from performance.forms.mixins import BackLinkMixin
from performance.forms.mixins import SubmitUpdateDeleteMixin

from ..models import PerformanceMeta

class PerformanceMetaForm(ModelForm):
    class Meta:
        model = PerformanceMeta
        only = ['assumed_best_lanes_quarter']
        field_args = {
            'assumed_best_lanes_quarter': {
                'label': 'Assumed Best Lanes for Quarter',
            }
        }
