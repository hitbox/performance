"""Reset scheduled_report_id_seq sequence

Restored from backups the primary key sequence was out of sync trying to add a
new scheduled report.

Revision ID: 47f19fc79434
Revises: 34f35c8bd527
Create Date: 2024-07-30 15:33:24.734178

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '47f19fc79434'
down_revision = '34f35c8bd527'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()

    table_name = 'scheduled_report'
    column_name = 'id'
    sequence_name = 'scheduled_report_id_seq'

    max_id_query = f'SELECT MAX({column_name}) FROM {table_name}'
    max_id = connection.execute(sa.text(max_id_query)).scalar()

    new_sequence_value = (max_id or 0) + 1

    setval_query = f"SELECT setval('{sequence_name}', {new_sequence_value})"
    connection.execute(sa.text(setval_query))

def downgrade():
    # no need to downgrade the sequence reset
    pass
