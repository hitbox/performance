"""is_lane on flight_type

Revision ID: 9a68c40ed6d3
Revises: 71cd7479c95c
Create Date: 2022-06-17 09:57:05.725155

"""
import os
import types

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '9a68c40ed6d3'
down_revision = '71cd7479c95c'
branch_labels = None
depends_on = None

# manually constructing what flask does automatically
PERFORMANCE_CONFIG = os.path.join('instance', os.environ['PERFORMANCE_CONFIG'])

app_config = types.ModuleType('config')
app_config.__file__ = PERFORMANCE_CONFIG
with open(PERFORMANCE_CONFIG, mode='rb') as config_file:
    exec(compile(config_file.read(), PERFORMANCE_CONFIG, 'exec'), app_config.__dict__)

metadata = sa.MetaData()

flight_type_table = sa.Table(
    'flight_type',
    metadata,
    sa.Column('name', sa.Integer, primary_key=True),
    sa.Column('is_lane', sa.Boolean),
)

def upgrade():
    op.add_column('flight_type',
        sa.Column('is_lane',
            sa.Boolean(),
            server_default='false',
            nullable=False))

    engine = op.get_bind()
    engine.execute(
        sa.update(flight_type_table)
        .values(
            is_lane = flight_type_table.c.name.in_(
                app_config.PERFORMANCE_LANES_FLIGHTTYPES
            )
        )
    )

def downgrade():
    op.drop_column('flight_type', 'is_lane')
