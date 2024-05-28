import sqlalchemy as sa

from sqlalchemy.ext.hybrid import hybrid_property

from performance import settings
from performance.extensions import db

BINDKEY = 'schedops'

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

    ac_registration = sa.Column(
        sa.String,
        nullable = True,
        comment = 'Registration of the aircraft', # tail number
    )

    dep_dt = sa.Column(
        sa.DateTime,
        nullable = False,
        comment = 'Actual time of departure  (ATA)',
    )

    arr_dt = sa.Column(
        sa.DateTime,
        nullable = False,
        comment = 'Actual time of arrival',
    )


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
            'Entry usage:   E=Estimated (Demand forcasted for the flight leg)  B=Booked (Bookings for the flight leg)  F=Flown (Flown Passengers for the flight leg)'
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
        return sa.func.round(cls.baggage_weight)

    @hybrid_property
    def baggage_weight_lbs(self):
        kg_to_lbs_factor = settings.kilogram_conversion_factor()
        return self.baggage_weight * kg_to_lbs_factor

    @baggage_weight_lbs.expression
    def baggage_weight_lbs(cls):
        kg_to_lbs_factor = settings.kilogram_conversion_factor()
        return cls.baggage_weight * kg_to_lbs_factor

    @hybrid_property
    def baggage_weight_lbs_integer(self):
        kg_to_lbs_factor = settings.kilogram_conversion_factor()
        return round(self.baggage_weight * kg_to_lbs_factor)

    @baggage_weight_lbs.expression
    def baggage_weight_lbs_integer(cls):
        kg_to_lbs_factor = settings.kilogram_conversion_factor()
        return sa.func.round(cls.baggage_weight * kg_to_lbs_factor)
