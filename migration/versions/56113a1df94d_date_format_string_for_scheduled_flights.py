"""Date format string for scheduled flights.

Revision ID: 56113a1df94d
Revises: f538884898ed
Create Date: 2025-09-17 13:40:24.558516

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '56113a1df94d'
down_revision = 'f538884898ed'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'scheduled_flight',
        sa.Column(
            'origin_departure_estimated_date_template',
            sa.String(),
            nullable=True,
        ),
    )
    op.add_column(
        'scheduled_flight',
        sa.Column(
            'destination_arrival_estimated_date_template',
            sa.String(),
            nullable=True,
        ),
    )

def downgrade():
    op.drop_column('scheduled_flight', 'destination_arrival_estimated_date_template')
    op.drop_column('scheduled_flight', 'origin_departure_estimated_date_template')
