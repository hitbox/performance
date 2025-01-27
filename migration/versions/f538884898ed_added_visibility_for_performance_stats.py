"""Added visibility for performance stats.

Revision ID: f538884898ed
Revises: b1d9e43c4515
Create Date: 2025-01-22 15:36:12.415076

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'f538884898ed'
down_revision = 'b1d9e43c4515'
branch_labels = None
depends_on = None

tables_for_show_columns = [
    'report',
    'scheduled_report',
]

new_show_columns = [
    'show_lanes',
    'show_chargeable_delays',
    'show_delays_gt_30_count',
    'show_on_time_performance_gt_15',
    'show_on_time_performance_gt_30',
    'show_flights_controllable_over_15',
    'show_flights_controllable_over_30',
]

def upgrade():
    op.alter_column(
        'flight',
        'report_id',
        existing_type = sa.INTEGER(),
        nullable = False,
    )

    # Add show_* columns to reports and scheduled reports.

    # Exceptional values we want going forward. Others default to true.
    values = {
        ('scheduled_report', 'show_on_time_performance_gt_30'): False,
        ('scheduled_report', 'show_flights_controllable_over_30'): False,
    }

    # Create new columns, temporarily nullable so we can fill them.
    for table_name in tables_for_show_columns:
        for column_name in new_show_columns:
            # Add new column.
            new_column = sa.Column(column_name, sa.Boolean(), nullable=True)
            op.add_column(table_name, new_column)
            # Update new column values, defaulting to True unless given in the values table.
            table = sa.sql.table(table_name, sa.sql.column(column_name, sa.Boolean()))
            new_value = values.get((table_name, column_name), True)
            op.execute(table.update().values(**{column_name: new_value}))
            # Update column to not-nullable.
            op.alter_column(table_name, column_name, nullable=False)

def downgrade():
    # Drop all the new show_* columns for all tables.
    for table_name in tables_for_show_columns:
        for column_name in new_show_columns:
            op.drop_column(table_name, column_name)

    op.alter_column(
        'flight',
        'report_id',
        existing_type = sa.INTEGER(),
        nullable = True,
    )
