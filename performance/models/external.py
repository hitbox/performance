import sqlalchemy as sa

from sqlalchemy import CHAR
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Integer
from sqlalchemy import String
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

    leg_no = Column(
        Integer,
        primary_key = True,
        comment = 'Number of Leg',
    )

    what_if = Column(
        String,
        primary_key = True,
        comment = 'Name of What-If',
    )

    leg_state = Column(
        String,
        comment =
            'State of Leg:'
            ' SKD - scheduled,'
            ' NEW - new,'
            ' NXI - next info,'
            ' ETD - estimated departure,'
            ' ISK - informative schedule,'
            ' OUT - off-block,'
            ' DEP - departed,'
            ' DIV - diverted,'
            ' ON - touch down,'
            ' ARR - arrived,'
            ' RTR - return to ramp,'
            ' RTO - return to original,'
            ' INC - incomplete,'
            ' CNL - cancelled,'
            ' DEL - deleted',
        info = {
            'states': {
                'SKD': 'scheduled',
                'NEW': 'new',
                'NXI': 'next info',
                'ETD': 'estimated departure',
                'ISK': 'informative schedule',
                'OUT': 'off-block',
                'DEP': 'departed',
                'DIV': 'diverted',
                'ON': 'touch down',
                'ARR': 'arrived',
                'RTR': 'return to ramp',
                'RTO': 'return to original',
                'INC': 'incomplete',
                'CNL': 'cancelled',
                'DEL': 'deleted',
            },
        },
    )

    @hybrid_property
    def leg_state_scheduled(self):
        return self.leg_state == 'SKD'

    @leg_state_scheduled.expression
    def leg_state_scheduled(cls):
        return cls.leg_state == 'SKD'

    @hybrid_property
    def leg_state_new(self):
        return self.leg_state == 'NEW'

    @leg_state_new.expression
    def leg_state_new(cls):
        return cls.leg_state == 'NEW'

    entry_dt = Column(
        Date,
        comment = 'Timestamp of the last update',
    )

    fn_carrier = Column(
        String,
        nullable = False,
        comment = 'Flight designator: carrier',
    )

    fn_number = Column(
        Integer,
        nullable = False,
        comment = 'Flight designator: number',
    )

    @hybrid_property
    def fn_number_as_string(self):
        return str(self.fn_number)

    @fn_number_as_string.expression
    def fn_number_as_string(cls):
        return sa.cast(cls.fn_number, String(4)).label('fn_number_as_string')

    ac_registration = Column(
        String,
        nullable = True,
        comment = 'Registration of the aircraft', # tail number
    )

    dep_ap_sched = Column(
        String,
        nullable = False,
        comment = 'Scheduled airport of departure   (IATA)',
    )

    dep_ap_actual = Column(
        String,
        nullable = False,
        comment = 'Actual airport of departure',
    )

    dep_dt = Column(
        DateTime,
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

    arr_ap_sched = Column(
        String,
        nullable = False,
        comment = 'Scheduled airport of arrival',
        # mistake in the database's comment field calls this departure
    )

    arr_ap_actual = Column(
        String,
        nullable = False,
        comment = 'Actual airport of arrival',
    )

    arr_dt = Column(
        DateTime,
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

    leg_no = Column(
        Integer,
        primary_key = True,
        comment = 'Leg number of the according leg',
    )

    usage = Column(
        String,
        primary_key = True,
        comment = (
            'Entry usage:'
            '   E=Estimated (Demand forcasted for the flight leg)'
            '  B=Booked (Bookings for the flight leg)'
            '  F=Flown (Flown Passengers for the flight leg)'
        ),
    )

    @hybrid_property
    def usage_flown(self):
        return self.usage == 'F'

    @usage_flown.expression
    def usage_flown(cls):
        return cls.usage == 'F'

    baggage_weight = Column(
        Float,
        comment = 'Baggage weight [kg] - load information code B',
    )

    gross_weight = Column(
        Integer,
        comment = 'Gross weight of the aircraft at departure',
    )

    zero_fuel_weight = Column(
        Integer,
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
            Integer,
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
            Integer,
        ).label('baggage_weight_lbs_integer')


class LegTimes(db.Model):
    """
    Actual times of a leg.
    """

    __bind_key__ = BINDKEY

    leg_no = Column(
        'leg_no',
        Integer,
        primary_key = True,
        comment = 'Leg number',
    )

    usage = Column(
        'usage',
        CHAR(1),
        nullable = False,
        primary_key = True,
        # Comment whitespace preserved from column comment.
        comment =
            'Entry usage:'
            '   F=Flight Log (times from flight log)'
            '  M=Movements (times from MVT-messages)'
            '  A=ACARS (times from ACARS-messages)'
            '  I=Irregularity'
            '  C=Movement Estimates'
            '   E=ACARS Estimates'
            ' D=system calculated MVT Estimates'
            '  G=system calculated ACARS Estimates'
            ' T=target times as defined by IATA/AIDX'
            ' B=Estimated Times from PSFlightMessages',
    )

    @hybrid_property
    def usage_movements(self):
        return usage == 'M'

    @usage_movements.expression
    def usage_movements(cls):
        return cls.usage == 'M'

    what_if = Column(
        'what_if',
        String(20),
        nullable = False,
        primary_key = True,
        comment = 'What If',
    )

    @hybrid_property
    def what_if_underscore(self):
        return self.what_if == '_'

    @what_if_underscore.expression
    def what_if_underscore(cls):
        return cls.what_if == '_'

    update_key = Column(
        'update_key',
        Integer,
        nullable = False,
        comment = 'Update key of the table',
    )

    leg_update_no = Column(
        'leg_update_no',
        Integer,
        nullable = False,
        default = 1,
    )

    offblock_dt = Column(
        'offblock_dt',
        DateTime,
        comment = 'Offblock time',
    )

    airborne_dt = Column(
        'airborne_dt',
        DateTime,
        comment = 'Take-off time',
    )

    landing_dt = Column(
        'landing_dt',
        DateTime,
        comment = 'Touch-down time',
    )

    onblock_dt = Column(
        'onblock_dt',
        DateTime,
        comment = 'Onblock time',
    )

    acars_init_dt = Column(
        'acars_init_dt',
        DateTime,
        comment = 'ACARS init time',
    )

    acars_doors_closed_dt = Column(
        'acars_doors_closed_dt',
        DateTime,
        comment = 'ACARS doors closed time',
    )

    mvt_after_pushback_dt = Column(
        'mvt_after_pushback_dt',
        DateTime,
        comment = 'Time of MVT after PushBack',
    )

    state = Column(
        'state',
        String(3),
        nullable = False,
        comment = 'the state of this entity ((N)ew, (U)pdate, (D)elete)',
    )

    startup_approval_dt = Column(
        'startup_approval_dt',
        DateTime,
        comment =
            'The time that an aircraft can expect to'
            ' receive start up / push back approval',
    )
