"""add ordering field to ScheduledReport

Revision ID: cc845af6fe92
Revises: 3b78c50e7d64
Create Date: 2022-02-07 07:08:08.023335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc845af6fe92'
down_revision = '3b78c50e7d64'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('scheduled_report', sa.Column('display_order', sa.Integer(), nullable=True))
    op.create_unique_constraint(None, 'scheduled_report', ['name'])


def downgrade():
    op.drop_constraint(None, 'scheduled_report', type_='unique')
    op.drop_column('scheduled_report', 'display_order')
