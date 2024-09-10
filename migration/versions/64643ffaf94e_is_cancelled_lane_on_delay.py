"""is_cancelled_lane on delay

Revision ID: 64643ffaf94e
Revises: 9a68c40ed6d3
Create Date: 2022-06-17 10:39:52.637853

"""
import os
import types

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '64643ffaf94e'
down_revision = '9a68c40ed6d3'
branch_labels = None
depends_on = None

# manually constructing what flask does automatically
PERFORMANCE_CONFIG = os.path.join('instance', os.environ['PERFORMANCE_CONFIG'])

app_config = types.ModuleType('config')
app_config.__file__ = PERFORMANCE_CONFIG
with open(PERFORMANCE_CONFIG, mode='rb') as config_file:
    exec(compile(config_file.read(), PERFORMANCE_CONFIG, 'exec'), app_config.__dict__)

metadata = sa.MetaData()

delay_table = sa.Table(
    'delay',
    metadata,
    sa.Column('code', sa.String, nullable=False),
    sa.Column('is_cancelled_lane', sa.Boolean),
)

def upgrade():
    """
    Add field to replace PERFORMANCE_LANES_INCLUDE_CANCELLED_DELAYS which was a
    list of codes that still count the flight as a lane when the code is
    cancelled.
    """
    op.add_column('delay',
        sa.Column(
            'is_cancelled_lane',
            sa.Boolean(),
            server_default='false',
            nullable=False
        )
    )
    # update new field
    engine = op.get_bind()

    engine.execute(
        sa.update(delay_table)
        .values(
            is_cancelled_lane = delay_table.c.code.in_(
                app_config.PERFORMANCE_LANES_INCLUDE_CANCELLED_DELAYS
            )
        )
        .where(
            delay_table.c.is_cancelled_lane is None,
        )
    )

def downgrade():
    op.drop_column('delay', 'is_cancelled_lane')
