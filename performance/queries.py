import sqlalchemy as sa

from flask import current_app

from . import models
from . import settings
from .extensions import db
from .utils import quarter_of_date

def get_external_stmt(report_date):
    """
    Query statement to get baggage weight from external source matching
    departure date against report date.
    """
    # NOTES
    # - before this mistake is made again, oracle does not have separate date
    #   and time types.
    external_stmt = (
        db.select(
            # flight number is string on this application's side
            models.Leg.fn_number_as_string,
            # datetimes broken apart into date and time, on the python side
            # dates and times and strings on the database side
            models.Leg.dep_dt_date_string,
            models.Leg.dep_dt_time_string,
            models.Leg.dep_ap_actual,
            models.Leg.arr_dt_date_string,
            models.Leg.arr_dt_time_string,
            models.Leg.arr_ap_actual,
            models.LegPax.baggage_weight_integer.label('baggage_weight_kg'),
            models.LegPax.baggage_weight_lbs_integer.label('baggage_weight_lbs'),
        )
        .outerjoin(
            models.LegPax,
            models.Leg.leg_no == models.LegPax.leg_no,
        )
        .where(
            models.Leg.dep_dt_date_string == str(report_date),
            # filter for airline
            models.Leg.fn_carrier == settings.external_fn_carrier(),
            # entry usage estimated, booked, and flown
            models.LegPax.usage == settings.external_usage(),
        )
    )
    return external_stmt

def get_internal_stmt(report_date):
    internal_flights_stmt = (
        db.select(
            models.Flight,
        )
        .join(
            models.Report,
        )
        .where(
            models.Report.date == report_date,
        )
    )
    return internal_flights_stmt

def get_scheduled_flight_type_instance():
    return models.FlightType.query.filter(models.FlightType.name == 'Scheduled').one()

def date_criteria(date):
    """
    Report from date criteria.
    """
    return models.Report.date == date

def month_to_date_criteria(date):
    """
    Select reports for a month to a date criteria.
    """
    expression = db.and_(
        db.func.date_part('year', models.Report.date) == date.year,
        db.func.date_part('month', models.Report.date) == date.month,
        models.Report.date <= date,
    )
    return expression

def quarter_to_date_criteria(date):
    """
    Select reporots for a quarter to a date criteria.
    """
    expression = db.and_(
        db.func.date_part('year', models.Report.date) == date.year,
        models.Report.date_quarter == quarter_of_date(date),
        models.Report.date <= date,
    )
    return expression

def lanes(date_criteria):
    """
    Select flights for `date_criteria` that are considered lanes.
    """
    stmt = (
        models.Flight.query
        .join(models.Report) # for date_criteria
        .join(models.FlightType)
        .filter(
            date_criteria,
            models.FlightType.is_lane == True,
        )
    )
    return stmt

def flights_with_controllable_destination_delays(date_criteria, over_minutes):
    """
    Select flights with controllable destination delays over given number of
    minutes, for a `date_criteria`.
    """
    controllable_destination_delay_over_minutes = (
        models.DestinationDelay.query
        .join(models.Delay)
        .filter(
            models.Flight.id == models.DestinationDelay.flight_id,
            models.Delay.is_controllable == True,
            models.DestinationDelay.minutes > over_minutes,
        )
    )
    flights_with_controllable_destination_delays_query = (
        models.Flight.query
        .join(models.Report) # for date_criteria
        .join(models.FlightType)
        .filter(
            date_criteria,
            models.FlightType.is_controllable == True,
            controllable_destination_delay_over_minutes.exists(),
        )
    )
    return flights_with_controllable_destination_delays_query

def performance_contract_query(date):
    """
    Select the performance contract for a date.
    """
    stmt = sa.select(
        models.Contract
    )
    if settings.contracts_use_date_range():
        stmt = stmt.where(
            date >= models.Contract.date_range_start,
            date <= models.Contract.date_range_end,
        )
    return stmt

def contract_range_criteria(date, contract):
    """
    Return the Report.date criteria for a given date and contract.
    """
    criteria = [
        models.Report.date <= date,
    ]
    if contract.date_range_start:
        criteria.append(
            models.Report.date >= contract.date_range_start,
        )
    return db.and_(*criteria)
