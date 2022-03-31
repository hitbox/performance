"""add assumed best for month

Revision ID: b80c49567a12
Revises: c5232a9c57bd
Create Date: 2021-08-18 04:12:40.612880

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'b80c49567a12'
down_revision = 'c5232a9c57bd'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('assumed_best',
        sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('lanes', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('assumed_best')
