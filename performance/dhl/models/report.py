from itertools import groupby

from performance.extensions import db
from performance.models.mixin import MetaMixin

from .bound import BoundRelationshipMixin
from .crewinfo import make_crew_info_column
from .operation import OperationRelationshipMixin
from .util import grouped_flights

class Report(
    BoundRelationshipMixin,
    MetaMixin,
    OperationRelationshipMixin,
    db.Model,
):
    """
    DHL Performance Report.
    """

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True)
    flights = db.relationship(
        'performance.dhl.models.flight.Flight',
        backref = 'report',
        cascade = 'all, delete-orphan',
    )

    # comments/details
    system_detail = db.Column(
        db.Text,
        info = dict(
            label = 'System Detail',
        ),
    )
    charter_detail = db.Column(
        db.Text,
        info = dict(
            label = 'Charter Detail',
        ),
    )
    extra_section_detail = db.Column(
        db.Text,
        info = dict(
            label = 'Extra Section Detail',
        ),
    )
    ferry_flight_detail = db.Column(
        db.Text,
        info = dict(
            label = 'Ferry Flight Detail',
        ),
    )

    aircraft_spares_1200 = db.Column(db.Integer, info=dict(label='1200'))
    aircraft_spares_1800 = db.Column(db.Integer)
    aircraft_spares_2000 = db.Column(db.Integer, info=dict(label='2000'))
    aircraft_spares_0300 = db.Column(db.Integer, info=dict(label='0300'))

    crew_info_1200 = make_crew_info_column('1200')
    crew_info_1800 = make_crew_info_column('1800')
    crew_info_2000 = make_crew_info_column('2000')
    crew_info_0300 = make_crew_info_column('0300')

    # ABX/Amazon performance numbers
    # NOTE: previous is actual today (legacy problem).
    abx_amazon_previous_days_performance_percent = db.Column(db.Float)
    abx_amazon_previous_days_performance_lanes = db.Column(db.Integer)
    abx_amazon_previous_days_performance_late = db.Column(db.Integer)
    abx_amazon_arrival_performance_mtd_percent = db.Column(db.Float)
    abx_amazon_arrival_performance_mtd_lanes = db.Column(db.Integer)
    abx_amazon_arrival_performance_mtd_late = db.Column(db.Integer)
    abx_amazon_days_at_100_percent = db.Column(db.Integer)
    abx_amazon_qtd_performance_percent = db.Column(db.Float)
    abx_amazon_qtd_performance_lanes = db.Column(db.Integer)
    abx_amazon_qtd_performance_late = db.Column(db.Integer)

    # DHL performance numbers
    dhl_previous_overall_performance = db.Column(db.Float)
    dhl_previous_overall_performance_lanes = db.Column(db.Integer)
    dhl_previous_overall_performance_late = db.Column(db.Integer)
    dhl_todays_arrival_performance_front_half = db.Column(db.Float)
    dhl_todays_arrival_performance_front_half_lanes = db.Column(db.Integer)
    dhl_todays_arrival_performance_front_half_late = db.Column(db.Integer)
    dhl_arrival_performance_mtd = db.Column(db.Float)
    dhl_arrival_performance_mtd_lanes = db.Column(db.Integer)
    dhl_arrival_performance_mtd_late = db.Column(db.Integer)
    dhl_assumed_best_arrival_performance_for_month_percent = db.Column(db.Float)

    # XXX: lanes and late unused?
    #      It does not look like these are used.
    dhl_assumed_best_arrival_performance_for_month_lanes = db.Column(db.Integer)
    dhl_assumed_best_arrival_performance_for_month_late = db.Column(db.Integer)
    dhl_arrival_performance_wtd = db.Column(db.Float)
    dhl_arrival_performance_wtd_lanes = db.Column(db.Integer)
    dhl_arrival_performance_wtd_late = db.Column(db.Integer)
    dhl_days_at_100_percent = db.Column(db.Integer)
    dhl_arrival_performance_mtd_30_percent = db.Column(db.Float)
    dhl_arrival_performance_mtd_30_lanes = db.Column(db.Integer)
    dhl_arrival_performance_mtd_30_late = db.Column(db.Integer)
    dhl_qtd_performance = db.Column(db.Float)
    dhl_qtd_performance_lanes = db.Column(db.Integer)
    dhl_qtd_performance_late = db.Column(db.Integer)

    def grouped_flights(self):
        return grouped_flights(self.flights)
