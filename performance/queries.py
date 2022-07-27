from flask import current_app

from .extensions import db
from .models import Contract
from .models import DestinationDelay
from .models import Flight
from .models import FlightType
from .models import Report
from .utils import quarter_of_date

def get_scheduled_flight_type_instance():
    return FlightType.query.filter(FlightType.name == 'Scheduled').one()

def date_criteria(date):
    """
    Report from date criteria.
    """
    return Report.date == date

def month_to_date_criteria(date):
    """
    Select reports for a month to a date criteria.
    """
    return db.and_(
        db.func.date_part('year', Report.date) == date.year,
        db.func.date_part('month', Report.date) == date.month,
        Report.date <= date)

def quarter_to_date_criteria(date):
    """
    Select reporots for a quarter to a date criteria.
    """
    return db.and_(
        db.func.date_part('year', Report.date) == date.year,
        Report.date_quarter == quarter_of_date(date),
        Report.date <= date)

def lanes(date_criteria):
    """
    Select flights for `date_criteria` that are considered lanes.
    """
    # last instruction was that lane count should always match the scheduled
    # table count which is just a count of the flights in it.
    return (Flight.query
        .join(Report) # for date_criteria
        .join(FlightType)
        .filter(
            date_criteria,
            FlightType.name.in_(
                current_app.config.get('PERFORMANCE_LANES_FLIGHTTYPES', [])
            )
        )
    )

def flights_with_controllable_destination_delays(date_criteria, over_minutes):
    """
    Select flights with controllable destination delays over given number of
    minutes, for a `date_criteria`.
    """
    return (Flight.query
        .join(Report) # for date_criteria
        .join(DestinationDelay)
        .filter(
            date_criteria,
            DestinationDelay.is_controllable == True,
            DestinationDelay.minutes > over_minutes,
        ))

def performance_contract_query(date):
    """
    Select the performance contract for a date.
    """
    return Contract.query.filter(
        Contract.date_range_start <= date,
        Contract.date_range_end >= date
    )

def contract_range_criteria(date, contract):
    """
    Return the Report.date criteria for a given date and contract.
    """
    return db.and_(
        Report.date >= contract.date_range_start,
        Report.date <= date,
    )
