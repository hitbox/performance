"""can_edit_schedule

Revision ID: 58ff3367afe5
Revises: cc845af6fe92
Create Date: 2022-03-31 07:30:05.631779

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '58ff3367afe5'
down_revision = 'cc845af6fe92'
branch_labels = None
depends_on = None

def upgrade():
    """
    Add flag to users indicating they can edit schedules.
    """
    op.add_column('user', sa.Column('can_edit_schedule', sa.Boolean(), nullable=True))

def downgrade():
    op.drop_column('user', 'can_edit_schedule')
