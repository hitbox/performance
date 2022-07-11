"""delay codes and associations

Revision ID: 71cd7479c95c
Revises: 5f9f2b0a2878
Create Date: 2022-06-16 08:46:41.579693

"""
import os
import re
import types

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '71cd7479c95c'
down_revision = '5f9f2b0a2878'
branch_labels = None
depends_on = None

# manually constructing what flask does automatically
PERFORMANCE_CONFIG = os.path.join('instance', os.environ['PERFORMANCE_CONFIG'])

app_config = types.ModuleType('config')
app_config.__file__ = PERFORMANCE_CONFIG
with open(PERFORMANCE_CONFIG, mode='rb') as config_file:
    exec(compile(config_file.read(), PERFORMANCE_CONFIG, 'exec'), app_config.__dict__)

metadata = sa.MetaData()

flight_table = sa.Table(
    'flight',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('origin_delays', sa.String), # legacy field
    sa.Column('destination_delays', sa.String), # legacy field
    sa.Column('legacy_origin_delays', sa.String), # save legacy field
    sa.Column('legacy_destination_delays', sa.String), # save legacy field
)

delay_table = sa.Table(
    'delay',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('code', sa.String, nullable=False),
    sa.Column('is_controllable', sa.Boolean, nullable=False),
    sa.Column('is_always_show', sa.Boolean, nullable=False),
)

origin_delay_table = sa.Table(
    'origin_delay',
    metadata,
    sa.Column('flight_id', sa.Integer, sa.ForeignKey('flight.id'), primary_key=True),
    sa.Column('delay_id', sa.Integer, sa.ForeignKey('flight.id'), primary_key=True),
    sa.Column('position', sa.Integer, primary_key=True),
    sa.Column('minutes', sa.Integer),
    sa.Column('is_cancelled', sa.Boolean),
    sa.Column('is_always_show', sa.Boolean),
)

destination_delay_table = sa.Table(
    'destination_delay',
    metadata,
    sa.Column('flight_id', sa.Integer, sa.ForeignKey('flight.id'), primary_key=True),
    sa.Column('delay_id', sa.Integer, sa.ForeignKey('flight.id'), primary_key=True),
    sa.Column('position', sa.Integer, primary_key=True),
    sa.Column('minutes', sa.Integer),
    sa.Column('is_cancelled', sa.Boolean),
)

CANCELLED = 'XLD'

_delaystring_re = re.compile(
    r'(?P<code>[a-zA-Z]{3})'
    r'\s*' # whitespace
    r'\(?' # optional left parenthesis
    r'\s*' # whitespace
    r'(?P<minutes>[0-9]*)?' # optional number of minutes
    r'\s*' # whitespace
    r'\)?' # optional right parenthesis
)

class Delay:
    """
    Simple object to hold the attributes of a flight delay, parsed from legacy strings.
    """

    def __init__(self, code, minutes, is_cancelled):
        self.code = code
        self.minutes = minutes
        self.is_cancelled = is_cancelled


def parse_delay_string(text):
    """
    Parse human data entry into a list of pairs of strings and minutes.
    """
    delays = []
    if text is not None:
        matches = iter(
                (code, int(minutes) if minutes else None)
                for code, minutes in _delaystring_re.findall(text))
        # interpret and convert into Delay objects.
        for code, minutes in matches:
            code = code.upper()
            if code == CANCELLED:
                # consume next match making cancelled=True
                for code, minutes in matches:
                    delay = Delay(code, minutes, True)
                    delays.append(delay)
                    break
                else:
                    delay = Delay(code, None, True)
                    delays.append(delay)
                # what if cancelled is the last code?
            else:
                # take as non-cancelled code
                delay = Delay(code, minutes, False)
                delays.append(delay)
    return delays

def insert_flight_delays(
    engine,
    flight_id,
    delays_string,
    code_cache,
    flight_delay_table,
):
    """
    Parse legacy delays string and insert new normalized design with
    association table.
    """
    for position, legacy_delay in enumerate(parse_delay_string(delays_string)):
        if legacy_delay.code not in code_cache:
            # insert delay code and update cache
            is_controllable = (
                legacy_delay.code in app_config.PERFORMANCE_CONTROLLABLE
            )
            is_always_show = (
                legacy_delay.code in app_config.ALWAYS_SHOW_DELAY_CODES
            )
            result = engine.execute(
                sa.insert(delay_table).values(
                    code = legacy_delay.code,
                    is_controllable = is_controllable,
                    is_always_show = is_always_show,
                )
            )
            delay_id = result.inserted_primary_key[0]
            code_cache[legacy_delay.code] = delay_id
        delay_id = code_cache[legacy_delay.code]
        # insert delay assoc
        result = engine.execute(
            sa.insert(flight_delay_table).values(
                flight_id = flight_id,
                delay_id = delay_id,
                position = position,
                minutes = legacy_delay.minutes,
                is_cancelled = legacy_delay.is_cancelled
            )
        )

def insert_new_flight_delays(engine):
    """
    Insert new normalized flight delays from old string fields.
    """
    # select all flights with delay strings
    query = sa.select(flight_table).where(
        sa.or_(
            flight_table.c.origin_delays != '',
            flight_table.c.destination_delays != '',
        )
    )
    # insert flight delays associations
    delay_tables = [origin_delay_table, destination_delay_table]
    code_cache = {}
    for row in engine.execute(query):
        flight_id, *delay_strings = row
        for delays_string, flight_delay_table in zip(delay_strings, delay_tables):
            insert_flight_delays(
                engine,
                flight_id,
                delays_string,
                code_cache,
                flight_delay_table
            )

def upgrade():
    op.create_table('delay',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('is_controllable', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_always_show', sa.Boolean(), server_default='false', nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('destination_delay',
        sa.Column('flight_id', sa.Integer(), nullable=False),
        sa.Column('delay_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('minutes', sa.Integer(), nullable=True),
        sa.Column('is_cancelled', sa.Boolean(), server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['delay_id'], ['delay.id'], ),
        sa.ForeignKeyConstraint(['flight_id'], ['flight.id'], ),
        sa.PrimaryKeyConstraint('flight_id', 'delay_id', 'position')
    )
    op.create_table('origin_delay',
        sa.Column('flight_id', sa.Integer(), nullable=False),
        sa.Column('delay_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('minutes', sa.Integer(), nullable=True),
        sa.Column('is_cancelled', sa.Boolean(), server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['delay_id'], ['delay.id'], ),
        sa.ForeignKeyConstraint(['flight_id'], ['flight.id'], ),
        sa.PrimaryKeyConstraint('flight_id', 'delay_id', 'position')
    )
    engine = op.get_bind()

    # "rename" old string delays columns
    op.add_column('flight',
        sa.Column('legacy_destination_delays', sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.add_column('flight',
        sa.Column('legacy_origin_delays', sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    engine.execute(
        sa.update(flight_table).values(
            legacy_origin_delays = flight_table.c.origin_delays,
            legacy_destination_delays = flight_table.c.destination_delays,
        )
    )

    insert_new_flight_delays(engine)

    op.drop_column('flight', 'origin_delays')
    op.drop_column('flight', 'destination_delays')

def downgrade():
    op.add_column('flight',
        sa.Column('destination_delays', sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.add_column('flight',
        sa.Column('origin_delays', sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.drop_table('origin_delay')
    op.drop_table('destination_delay')
    op.drop_table('delay')
    op.drop_column('flight', 'legacy_origin_delays')
    op.drop_column('flight', 'legacy_destination_delays')
