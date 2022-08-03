"""make year and month primary key for assumed best

Revision ID: a99e4cbb8dca
Revises: ace3786c38a0
Create Date: 2022-08-03 15:02:35.023757

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'a99e4cbb8dca'
down_revision = 'ace3786c38a0'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_column('assumed_best', 'id')
    op.create_primary_key(
        'pk_assumed_best', 'assumed_best',
        ['year', 'month']
    )

def downgrade():
    op.add_column(
        'assumed_best',
        sa.Column(
            'id', sa.INTEGER(), autoincrement=True, nullable=False
        )
    )
