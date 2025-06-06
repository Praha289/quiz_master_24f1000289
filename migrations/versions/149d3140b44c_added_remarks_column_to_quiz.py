"""Added remarks column to Quiz

Revision ID: 149d3140b44c
Revises: f56c6123378c
Create Date: 2025-03-19 21:39:49.028472

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '149d3140b44c'
down_revision = 'f56c6123378c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quiz', schema=None) as batch_op:
        batch_op.add_column(sa.Column('remarks', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quiz', schema=None) as batch_op:
        batch_op.drop_column('remarks')

    # ### end Alembic commands ###
