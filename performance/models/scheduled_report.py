from performance.extensions import db
from performance.models.mixin import MetaMixin

class ScheduledReport(
    MetaMixin,
    db.Model,
):
    """
    Scheduled reports hold minimal flights to populate new reports on the
    effective datetime start.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    display_order = db.Column(db.Integer)

    scheduled_flights = db.relationship(
        'ScheduledFlight',
        back_populates = 'scheduled_report',
    )
