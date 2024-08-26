"""application metadata

Revision ID: 25d182d4de1f
Revises: c6a420d0b240
Create Date: 2024-08-20 09:38:23.063632

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '25d182d4de1f'
down_revision = 'c6a420d0b240'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'performance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('default_flight_type_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['default_flight_type_id'], ['flight_type.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # update default_flight_type_id to whatever
    op.execute(sa.text('INSERT INTO performance (default_flight_type_id) VALUES (1)'))

def downgrade():
    op.drop_table('performance')
