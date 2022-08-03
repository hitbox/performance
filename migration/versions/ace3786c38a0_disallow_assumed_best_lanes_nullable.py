"""disallow assumed best lanes nullable

Revision ID: ace3786c38a0
Revises: 4b640e6e49dd
Create Date: 2022-08-03 12:14:18.919639

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'ace3786c38a0'
down_revision = '4b640e6e49dd'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column('assumed_best', 'lanes',
               existing_type=sa.INTEGER(),
               nullable=False)

def downgrade():
    op.alter_column('assumed_best', 'lanes',
               existing_type=sa.INTEGER(),
               nullable=True)
