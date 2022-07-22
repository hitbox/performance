"""
fix and cleanup contracts and tiers

Revision ID: 78794610b8bf
Revises: 64643ffaf94e
Create Date: 2022-07-19 09:42:27.456009

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '78794610b8bf'
down_revision = '64643ffaf94e'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column(
        'assumed_best', 'month',
        existing_type=sa.INTEGER(),
        nullable=False
    )
    op.alter_column(
        'assumed_best', 'year',
        existing_type=sa.INTEGER(),
        nullable=False
    )
    op.alter_column(
        'contract',
        'name',
        existing_type=sa.VARCHAR(),
        nullable=False
    )
    op.alter_column(
        'performance_tier',
        'tier',
        existing_type=sa.INTEGER(),
        nullable=False
    )
    op.drop_column('performance_tier', 'order')

def downgrade():
    op.add_column(
        'performance_tier',
        sa.Column('order', sa.INTEGER(), autoincrement=False, nullable=True)
    )
    op.alter_column(
        'performance_tier',
        'tier',
        existing_type=sa.INTEGER(),
        nullable=True
    )
    op.alter_column(
        'contract',
        'name',
        existing_type=sa.VARCHAR(),
        nullable=True
    )
    op.alter_column(
        'assumed_best',
        'year',
        existing_type=sa.INTEGER(),
        nullable=True
    )
    op.alter_column(
        'assumed_best',
        'month',
        existing_type=sa.INTEGER(),
        nullable=True
    )
