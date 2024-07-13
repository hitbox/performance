import sqlalchemy as sa

from sqlalchemy.ext.hybrid import hybrid_property

from performance import settings
from performance.extensions import db

BINDKEY = 'schedops'

def date_part_expression(column):
    # return date part of an oracle datetime field
    return sa.func.to_char(column, 'YYYY-MM-DD')

def time_part_expression(column):
    # return time part of an oracle datetime field
    return sa.func.to_char(column, 'HH24:MI:SS')

class Leg(db.Model):
    """
    Leg Basic Data
    """

    __bind_key__ = BINDKEY

    leg_no = sa.Column(
        sa.Integer,
        primary_key = True,
        comment = 'Number of Leg',
    )

    what_if = sa.Column(
        sa.String,
        primary_key = True,
        comment = 'Name of What-If',
    )

    fn_carrier = sa.Column(
        sa.String,
        nullable = False,
        comment = 'Flight designator: carrier',
    )

    fn_number = sa.Column(
        sa.Integer,
        nullable = False,
        comment = 'Flight designator: number',
    )

    @hybrid_property
    def fn_number_as_string(self):
        return str(self.fn_number)

    @fn_number_as_string.expression
    def fn_number_as_string(cls):
        return sa.cast(cls.fn_number, sa.String(4)).label('fn_number_as_string')

    ac_registration = sa.Column(
        sa.String,
        nullable = True,
        comment = 'Registration of the aircraft', # tail number
    )

    dep_ap_sched = sa.Column(
        sa.String,
        nullable = False,
        comment = 'Scheduled airport of departure   (IATA)',
    )

    dep_ap_actual = sa.Column(
        sa.String,
        nullable = False,
        comment = 'Actual airport of departure',
    )

    dep_dt = sa.Column(
        sa.DateTime,
        nullable = False,
        comment = 'Actual time of departure  (ATA)',
        info = dict(
            label = 'ATA',
        ),
    )

    @hybrid_property
    def dep_dt_date_string(self):
        return str(self.dep_dt.date())

    @dep_dt_date_string.expression
    def dep_dt_date_string(cls):
        return date_part_expression(cls.dep_dt).label('dep_dt_date_string')

    @hybrid_property
    def dep_dt_time_string(self):
        return str(dep_dt.time())

    @dep_dt_time_string.expression
    def dep_dt_time_string(cls):
        return time_part_expression(cls.dep_dt).label('dep_dt_time_string')

    arr_ap_sched = sa.Column(
        sa.String,
        nullable = False,
        comment = 'Scheduled airport of arrival',
        # mistake in the database's comment field calls this departure
    )

    arr_ap_actual = sa.Column(
        sa.String,
        nullable = False,
        comment = 'Actual airport of arrival',
    )

    arr_dt = sa.Column(
        sa.DateTime,
        nullable = False,
        comment = 'Actual time of arrival',
    )

    @hybrid_property
    def arr_dt_date_string(self):
        return str(self.arr_dt.date())

    @arr_dt_date_string.expression
    def arr_dt_date_string(cls):
        return date_part_expression(cls.arr_dt).label('arr_dt_date_string')

    @hybrid_property
    def arr_dt_time_string(self):
        return self.arr_dt.time()

    @arr_dt_time_string.expression
    def arr_dt_time_string(cls):
        return time_part_expression(cls.arr_dt).label('arr_dt_time_string')


class LegPax(db.Model):
    """
    Passenger, crew, cargo and mail attribute of a leg.
    """

    __bind_key__ = BINDKEY

    leg_no = sa.Column(
        sa.Integer,
        primary_key = True,
        comment = 'Leg number of the according leg',
    )

    usage = sa.Column(
        sa.String,
        primary_key = True,
        comment = (
            'Entry usage:   E=Estimated (Demand forcasted for the flight leg)'
            '  B=Booked (Bookings for the flight leg)  F=Flown (Flown'
            ' Passengers for the flight leg)'
        ),
    )

    baggage_weight = sa.Column(
        sa.Float,
        comment = 'Baggage weight [kg] - load information code B',
    )

    gross_weight = sa.Column(
        sa.Integer,
        comment = 'Gross weight of the aircraft at departure',
    )

    zero_fuel_weight = sa.Column(
        sa.Integer,
        comment = (
            'Weight of the airplane and all its contents, minus the total'
            ' weight of the fuel on board.'
        ),
    )

    @hybrid_property
    def baggage_weight_integer(self):
        return round(self.baggage_weight)

    @baggage_weight_integer.expression
    def baggage_weight_integer(cls):
        return sa.cast(
            sa.func.round(
                cls.baggage_weight
            ),
            sa.Integer,
        ).label('baggage_weight_integer')

    @hybrid_property
    def baggage_weight_lbs(self):
        kg_to_lbs_factor = settings.kilogram_conversion_factor()
        return self.baggage_weight * kg_to_lbs_factor

    @baggage_weight_lbs.expression
    def baggage_weight_lbs(cls):
        kg_to_lbs_factor = settings.kilogram_conversion_factor()
        return (
            cls.baggage_weight * kg_to_lbs_factor
        ).label('baggage_weight_lbs')

    @hybrid_property
    def baggage_weight_lbs_integer(self):
        kg_to_lbs_factor = settings.kilogram_conversion_factor()
        return round(self.baggage_weight * kg_to_lbs_factor)

    @baggage_weight_lbs.expression
    def baggage_weight_lbs_integer(cls):
        kg_to_lbs_factor = settings.kilogram_conversion_factor()
        return sa.cast(
            sa.func.round(
                cls.baggage_weight * kg_to_lbs_factor
            ),
            sa.Integer,
        ).label('baggage_weight_lbs_integer')
