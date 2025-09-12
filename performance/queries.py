from datetime import timedelta

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
from .models import LegTimes
from .models import Report
from .utils import quarter_of_date

_exclude_leg_state_default = object()

def get_external_stmt(report_date, exclude_leg_state=_exclude_leg_state_default):
    """
    Return select for external flight data.
    """
    if exclude_leg_state is _exclude_leg_state_default:
        exclude_leg_state = ('NEW', 'SKD')
    external_stmt = db.select(
        # flight number is string on this application's side
        Leg.ac_registration.label('tail_number_with_prefix'),
        Leg.fn_number_as_string.label('flight_number'),
        Leg.dep_ap_actual.label('origin_station'),
        Leg.arr_ap_actual.label('destination_station'),
        LegPax.baggage_weight_lbs_integer.label('weight'),
        LegTimes.offblock_dt.label('actual_departure_datetime'),
        LegTimes.onblock_dt.label('actual_arrival_datetime'),
    ).outerjoin(
        LegPax,
        Leg.leg_no == LegPax.leg_no,
    ).outerjoin(
        LegTimes,
        LegTimes.leg_no == Leg.leg_no,
    ).where(
        # filter for airline
        Leg.fn_carrier == settings.external_fn_carrier(),
        LegPax.usage_flown,
        LegTimes.usage_movements,
        LegTimes.what_if_underscore,
        # Compare as range for maximum database compatibility.
        Leg.dep_dt >= report_date,
        Leg.dep_dt < report_date + timedelta(days=1)
    )
    if exclude_leg_state:
        external_stmt = external_stmt.where(
            Leg.leg_state.not_in(exclude_leg_state)
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
