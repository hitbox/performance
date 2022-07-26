"""add unique constraint on delay code string field.

Revision ID: 4b640e6e49dd
Revises: 78794610b8bf
Create Date: 2022-07-26 02:54:39.839220

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '4b640e6e49dd'
down_revision = '78794610b8bf'
branch_labels = None
depends_on = None

def upgrade():
    op.create_unique_constraint(None, 'delay', ['code'])

def downgrade():
    op.drop_constraint(None, 'delay', type_='unique')
