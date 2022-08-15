"""add is_lane flag to flight_type

Revision ID: 6f05ddeb64f1
Revises: b7df738fcb4c
Create Date: 2022-08-15 04:01:29.791484

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '6f05ddeb64f1'
down_revision = 'b7df738fcb4c'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column(
        'flight_type',
        sa.Column(
            'is_lane',
            sa.Boolean(),
            server_default='false',
            nullable=False
        )
    )

def downgrade():
    op.drop_column('flight_type', 'is_lane')
