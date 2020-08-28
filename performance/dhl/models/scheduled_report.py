from itertools import groupby

from performance.extensions import db
from performance.models.mixin import MetaMixin

from .operation import OperationRelationshipMixin
from .util import grouped_flights

class ScheduledReport(
    MetaMixin,
    OperationRelationshipMixin,
    db.Model,
):
    """
    DHL Scheduled reports hold minimal flights to populate new reports on the
    effective datetime start.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    scheduled_flights = db.relationship(
        'performance.dhl.models.scheduled_flight.ScheduledFlight',
        backref = 'scheduled_report',
    )

    def grouped_flights(self):
        """
        """
        return grouped_flights(self.scheduled_flights)
