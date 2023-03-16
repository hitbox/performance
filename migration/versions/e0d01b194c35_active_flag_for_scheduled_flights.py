"""active flag for scheduled flights

Revision ID: e0d01b194c35
Revises: 6f05ddeb64f1
Create Date: 2023-03-16 00:55:53.820008

Incident: 45836
Reason: Allow easily enable and disable scheduled flights, rather than having
        to create and delete them.
"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'e0d01b194c35'
down_revision = '6f05ddeb64f1'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column(
        'scheduled_flight',
        sa.Column(
            'is_active',
            sa.Boolean(),
            server_default = 'TRUE',
            nullable = False,
        )
    )

def downgrade():
    op.drop_column('scheduled_flight', 'is_active')
