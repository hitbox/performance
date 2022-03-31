"""move assumbed best lanes for quarter

Revision ID: c5232a9c57bd
Revises: 
Create Date: 2021-06-23 07:30:19.309253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5232a9c57bd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('performance_meta',
        sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('assumed_best_lanes_quarter', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column('report', sa.Column('performance_meta_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'report', 'performance_meta', ['performance_meta_id'], ['id'])
    op.drop_column('report', 'assumed_best_lanes')

def downgrade():
    op.add_column('report', sa.Column('assumed_best_lanes', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'report', type_='foreignkey')
    op.drop_column('report', 'performance_meta_id')
    op.drop_table('performance_meta')
