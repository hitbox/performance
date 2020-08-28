from performance.extensions import db
from performance.models.mixin import MetaMixin

from .util import grouped_flights

class Report(
    MetaMixin,
    db.Model,
):
    """
    Amazon Performance Report.
    """

    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.Date)
    flights = db.relationship(
        'performance.amazon.models.flight.Flight',
        backref = 'report',
        cascade = 'all,delete-orphan',
    )
    system_detail = db.Column(
        db.Text,
        info = dict(
            label = 'System Detail',
        ),
    )

    # NOTE: previous is actual today (legacy problem).
    previous_days_performance_percent = db.Column(db.Float)
    previous_days_performance_lanes = db.Column(db.Integer)
    previous_days_performance_late = db.Column(db.Integer)

    arrival_performance_mtd_percent = db.Column(db.Float)
    arrival_performance_mtd_lanes = db.Column(db.Integer)
    arrival_performance_mtd_late = db.Column(db.Integer)

    days_at_100_percent = db.Column(db.Integer)

    qtd_performance_percent = db.Column(db.Float)
    qtd_performance_lanes = db.Column(db.Integer)
    qtd_performance_late = db.Column(db.Integer)

    assumed_best_arrival_performance_for_month_percent = db.Column(db.Float)
    assumed_best_arrival_performance_for_month_lanes = db.Column(db.Integer)
    assumed_best_arrival_performance_for_month_late = db.Column(db.Integer)

    arrival_performance_mtd_30_percent = db.Column(db.Float)
    arrival_performance_mtd_30_lanes = db.Column(db.Integer)
    arrival_performance_mtd_30_late = db.Column(db.Integer)

    def grouped_flights(self):
        return grouped_flights(self.flights)
