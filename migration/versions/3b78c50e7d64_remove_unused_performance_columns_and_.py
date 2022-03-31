"""remove unused performance columns and tables; and enforce unique report date

Revision ID: 3b78c50e7d64
Revises: b80c49567a12
Create Date: 2021-09-21 09:24:14.051561

"""
import sqlalchemy as sa

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3b78c50e7d64'
down_revision = 'b80c49567a12'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_constraint('report_performance_meta_id_fkey', 'report', type_='foreignkey')
    op.drop_table('performance_meta')
    op.create_unique_constraint(None, 'report', ['date'])
    op.drop_column('report', 'arrival_performance_mtd_lanes')
    op.drop_column('report', 'assumed_best_arrival_performance_for_month_late')
    op.drop_column('report', 'assumed_best_arrival_performance_for_month_percent')
    op.drop_column('report', 'previous_days_performance_lanes')
    op.drop_column('report', 'qtd_performance_late')
    op.drop_column('report', 'arrival_performance_mtd_30_lanes')
    op.drop_column('report', 'arrival_performance_mtd_30_late')
    op.drop_column('report', 'arrival_performance_mtd_percent')
    op.drop_column('report', 'assumed_best_arrival_performance_for_month_lanes')
    op.drop_column('report', 'previous_days_performance_percent')
    op.drop_column('report', 'arrival_performance_mtd_late')
    op.drop_column('report', 'days_at_100_percent')
    op.drop_column('report', 'qtd_performance_percent')
    op.drop_column('report', 'arrival_performance_mtd_30_percent')
    op.drop_column('report', 'qtd_performance_lanes')
    op.drop_column('report', 'previous_days_performance_late')
    op.drop_column('report', 'performance_meta_id')

def downgrade():
    op.add_column('report', sa.Column('performance_meta_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('previous_days_performance_late', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('qtd_performance_lanes', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('arrival_performance_mtd_30_percent', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('qtd_performance_percent', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('days_at_100_percent', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('arrival_performance_mtd_late', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('previous_days_performance_percent', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('assumed_best_arrival_performance_for_month_lanes', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('arrival_performance_mtd_percent', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('arrival_performance_mtd_30_late', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('arrival_performance_mtd_30_lanes', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('qtd_performance_late', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('previous_days_performance_lanes', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('assumed_best_arrival_performance_for_month_percent', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('assumed_best_arrival_performance_for_month_late', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('report', sa.Column('arrival_performance_mtd_lanes', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('report_performance_meta_id_fkey', 'report', 'performance_meta', ['performance_meta_id'], ['id'])
    op.drop_constraint(None, 'report', type_='unique')
    op.create_table('performance_meta',
        sa.Column('created', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
        sa.Column('updated', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('assumed_best_lanes_quarter', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='performance_meta_pkey')
    )
