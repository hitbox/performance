"""
add tier range operator fields

Revision ID: 34f35c8bd527
Revises: e0d01b194c35
Create Date: 2023-05-05 02:44:10.426973

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '34f35c8bd527'
down_revision = 'e0d01b194c35'
branch_labels = None
depends_on = None

def upgrade():
    """
    Add fields to allow arbitrary comparison operators for each tier. Values
    default to originally hard-coded less-than and greater-than.
    """
    op.add_column(
        'performance_tier',
        sa.Column(
            'performance_operator_start',
            sa.Integer(),
            sa.CheckConstraint(
                f'performance_operator_start BETWEEN 1 and 5'
            ),
            server_default='5',
            nullable=False
        )
    )
    op.add_column(
        'performance_tier',
        sa.Column(
            'performance_operator_end',
            sa.Integer(),
            sa.CheckConstraint(
                f'performance_operator_end BETWEEN 1 and 5'
            ),
            server_default='1',
            nullable=False
        )
    )

def downgrade():
    op.drop_column('performance_tier', 'performance_operator_end')
    op.drop_column('performance_tier', 'performance_operator_start')
