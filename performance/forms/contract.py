import sqlalchemy as sa

from flask import request
from wtforms import FieldList
from wtforms import FormField
from wtforms import HiddenField
from wtforms_alchemy import ClassMap
from wtforms_alchemy import QuerySelectField

from ..models import Contract
from ..models import PerformanceTier

from . import defaults
from .base import ModelForm
from .fields import DelayCodesField
from .fields import StringTimeField
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin

class PerformanceTierForm(
    BackLinkMixin,
    ModelForm,
    SubmitUpdateDeleteMixin,
):
    """
    Arrival Performance tier for a performance range.
    """
    class Meta:
        model = PerformanceTier
        only = [
            'order',
            'tier',
            'performance_range_start',
            'performance_range_end',
        ]
        fields_order = [
            'order',
            'tier',
            'performance_range_start',
            'performance_range_end',
            'submit',
            'delete',
        ]


class ContractForm(
    BackLinkMixin,
    ModelForm,
    SubmitUpdateDeleteMixin,
):
    """
    Arrival Performance Contract for a date range.
    """
    class Meta:
        model = Contract
        only = [
            'name',
            'date_range_start',
            'date_range_end',
        ]
        fields_order = [
            'name',
            'date_range_start',
            'date_range_end',
            'submit',
            'delete',
        ]
