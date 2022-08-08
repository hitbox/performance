"""add description for delay codes

Revision ID: 8ad9e13b0a16
Revises: a99e4cbb8dca
Create Date: 2022-08-08 04:39:52.924937

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '8ad9e13b0a16'
down_revision = 'a99e4cbb8dca'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('delay', sa.Column('description', sa.String(), nullable=True))

def downgrade():
    op.drop_column('delay', 'description')
