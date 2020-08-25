import enum

from collections import defaultdict
from itertools import groupby
from operator import attrgetter

from sqlalchemy_utils import ChoiceType

from ...extensions import db
from ...sorting import flight_sort_key
from ...models.flight_type import FlightType
from ...models.mixin import MetaMixin

from .bound import BoundRelationshipMixin
from .operation import OperationRelationshipMixin

flightsortkey = attrgetter('bound', 'flight_type', 'flight_number_as_int')
flightgroupkey = attrgetter('bound', 'flight_type')

class CrewInfo(enum.Enum):
    FULL_CREW = 0
    CAPTAIN_ONLY = 1
    FIRST_OFFICER_ONLY = 2
    NONE = 3

    def __str__(self):
        return self.label


CrewInfo.FULL_CREW.label = 'Full Crew'
CrewInfo.CAPTAIN_ONLY.label = 'Captain Only'
CrewInfo.FIRST_OFFICER_ONLY.label = 'First Officer Only'
CrewInfo.NONE.label = '(None)'

def make_crew_info_column(label):
    return db.Column(
        ChoiceType(
            CrewInfo,
            impl = db.Integer()),
        default = CrewInfo.NONE,
        info = dict(
            label = label,
        )
    )

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
    date = db.Column(db.Date)
    flights = db.relationship('performance.dhl.models.flight.Flight',
                              backref='report', cascade='all,delete-orphan')

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
        return groupby(sorted(self.flights, key=flightsortkey), flightgroupkey)


class ScheduledReport(
    MetaMixin,
    OperationRelationshipMixin,
    db.Model,
):
    """
    Scheduled reports hold minimal flights to populate new reports on the
    effective datetime start.
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    scheduled_flights = db.relationship(
        'performance.dhl.models.flight.ScheduledFlight',
        backref='scheduled_report')

    def grouped_flights(self):
        """
        """
        return groupby(sorted(self.scheduled_flights, key=flightsortkey), flightgroupkey)
