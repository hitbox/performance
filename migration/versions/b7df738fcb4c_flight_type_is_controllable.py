"""add flight_type is_controllable, remove is_lane

Revision ID: b7df738fcb4c
Revises: 8ad9e13b0a16
Create Date: 2022-08-12 02:07:17.332738

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'b7df738fcb4c'
down_revision = '8ad9e13b0a16'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column(
        'flight_type',
        sa.Column(
            'is_controllable',
            sa.Boolean(),
            server_default='false',
            nullable=False,
        )
    )
    op.drop_column('flight_type', 'is_lane')

def downgrade():
    op.add_column(
        'flight_type',
        sa.Column(
            'is_lane',
            sa.BOOLEAN(),
            server_default=sa.text('false'),
            autoincrement=False,
            nullable=False,
        )
    )
    op.drop_column('flight_type', 'is_controllable')
