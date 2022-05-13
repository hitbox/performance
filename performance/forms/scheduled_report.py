import sqlalchemy as sa

from wtforms import HiddenField
from wtforms import StringField
from wtforms import IntegerField
from wtforms import SubmitField
from wtforms_alchemy import ClassMap
from wtforms_alchemy import QuerySelectField

from ..models import FlightType
from ..models import ScheduledFlight
from ..models import ScheduledReport

from . import defaults
from .base import BaseFlaskForm
from .fields import StringTimeField
from .mixins import BackLinkMixin
from .mixins import SubmitUpdateDeleteMixin

class ScheduledReportForm(
    BackLinkMixin,
    BaseFlaskForm,
):
    name = StringField('Name', render_kw=dict(placeholder='Scheduled Report Name'))
    display_order = IntegerField('Order')

    update = SubmitField('Update')
    delete = SubmitField('Delete')
