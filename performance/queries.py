import sqlalchemy as sa

from flask import current_app

from . import settings
from .extensions import db
from .models import Contract
from .models import Delay
from .models import DestinationDelay
from .models import FakeFlight
from .models import Flight
from .models import FlightType
from .models import Leg
from .models import LegPax
from .models import Report
from .utils import quarter_of_date

def get_external_stmt(report_date):
    """
    Query statement to get baggage weight from external source matching
    departure date against report date.
    """
    external_stmt = db.select(
        # flight number is string on this application's side
        Leg.fn_number_as_string,
        # datetimes broken apart into date and time, on the python side dates
        # and times and strings on the database side
        Leg.dep_dt_date_string,
        Leg.dep_dt_time_string,
        Leg.dep_ap_actual,
        Leg.arr_dt_date_string,
        Leg.arr_dt_time_string,
        Leg.arr_ap_actual,
        LegPax.baggage_weight_integer.label('baggage_weight_kg'),
        LegPax.baggage_weight_lbs_integer.label('baggage_weight_lbs'),
    ).outerjoin(
        LegPax,
        Leg.leg_no == LegPax.leg_no,
    ).where(
        Leg.dep_dt_date_string == str(report_date),
        # filter for airline
        Leg.fn_carrier == settings.external_fn_carrier(),
        # entry usage estimated, booked, and flown
        LegPax.usage == settings.external_usage(),
    )
    return external_stmt

def get_internal_stmt(report_date):
    internal_flights_stmt = (
        db.select(Flight)
        .join(Report)
        .where(Report.date == report_date)
    )
    return internal_flights_stmt

def get_scheduled_flight_type_instance():
    stmt = (
        sa.select(FlightType)
        .where(
            sa.func.lcase(FlightType.name) == 'scheduled',
        )
    )
    return db.session.scalars(stmt).one()

def date_criteria(date):
    """
    Report from date criteria.
    """
    return Report.date == date

def month_to_date_criteria(date):
    """
    Select reports for a month to a date criteria.
    """
    expression = db.and_(
        db.func.date_part('year', Report.date) == date.year,
        db.func.date_part('month', Report.date) == date.month,
        Report.date <= date,
    )
    return expression

def quarter_to_date_criteria(date):
    """
    Select reporots for a quarter to a date criteria.
    """
    expression = db.and_(
        db.func.date_part('year', Report.date) == date.year,
        Report.date_quarter == quarter_of_date(date),
        Report.date <= date,
    )
    return expression

def lanes(date_criteria):
    """
    Select flights for `date_criteria` that are considered lanes.
    """
    stmt = (
        db.select(Flight)
        .join(Report) # for date_criteria
        .join(FlightType)
        .where(
            date_criteria,
            FlightType.is_lane == True,
        )
    )
    return stmt

def flights_with_controllable_destination_delays(date_criteria, over_minutes):
    """
    Select flights with controllable destination delays over given number of
    minutes, for a `date_criteria`.
    """
    controllable_destination_delay_over_minutes = (
        db.select(DestinationDelay)
        .join(Delay)
        .where(
            Flight.id == DestinationDelay.flight_id,
            Delay.is_controllable == True,
            DestinationDelay.minutes > over_minutes,
        )
    )
    flights_with_controllable_destination_delays_query = (
        db.select(Flight)
        .join(Report) # for date_criteria
        .join(FlightType)
        .where(
            date_criteria,
            FlightType.is_controllable == True,
            controllable_destination_delay_over_minutes.exists(),
        )
    )
    return flights_with_controllable_destination_delays_query

def performance_contract_query(date):
    """
    Select the performance contract for a date.
    """
    stmt = sa.select(Contract)
    if settings.contracts_use_date_range():
        stmt = stmt.where(
            date >= Contract.date_range_start,
            date <= Contract.date_range_end,
        )
    return stmt

def contract_range_criteria(date, contract):
    """
    Return the Report.date criteria for a given date and contract.
    """
    criteria = [
        Report.date <= date,
    ]
    if contract.date_range_start:
        criteria.append(
            Report.date >= contract.date_range_start,
        )
    return db.and_(*criteria)
