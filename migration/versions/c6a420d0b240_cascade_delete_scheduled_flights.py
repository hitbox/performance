"""Cascade delete scheduled flights.

Revision ID: c6a420d0b240
Revises: 47f19fc79434
Create Date: 2024-07-31 05:12:05.994616
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'c6a420d0b240'
down_revision = '47f19fc79434'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_constraint(
        'scheduled_flight_scheduled_report_id_fkey',
        'scheduled_flight',
        type_ = 'foreignkey',
    )
    op.create_foreign_key(
        None,
        'scheduled_flight',
        'scheduled_report',
        ['scheduled_report_id'],
        ['id'],
        ondelete = 'CASCADE',
    )

def downgrade():
    op.drop_constraint(
        None,
        'scheduled_flight',
        type_ = 'foreignkey',
    )
    op.create_foreign_key(
        'scheduled_flight_scheduled_report_id_fkey',
        'scheduled_flight',
        'scheduled_report',
        ['scheduled_report_id'],
        ['id'],
    )
