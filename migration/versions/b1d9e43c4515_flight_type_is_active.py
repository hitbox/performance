"""flight type is_active

Revision ID: b1d9e43c4515
Revises: 25d182d4de1f
Create Date: 2024-08-23 11:11:13.222468

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'b1d9e43c4515'
down_revision = '25d182d4de1f'
branch_labels = None
depends_on = None

def upgrade():
    # disallow null names
    op.alter_column(
        'flight_type',
        'name',
        existing_type = sa.VARCHAR(),
        nullable = False,
    )
    # add new is_active column
    op.add_column(
        'flight_type',
        sa.Column(
            'is_active',
            sa.Boolean(),
            server_default='true',
            nullable=False,
        ),
    )
    #  update new is_active to true
    op.execute(sa.text('UPDATE flight_type SET is_active = true'))

def downgrade():
    op.alter_column(
        'flight_type',
        'name',
        existing_type = sa.VARCHAR(),
        nullable = True,
    )
    op.drop_column('flight_type', 'is_active')
