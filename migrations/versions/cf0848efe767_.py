"""empty message

Revision ID: cf0848efe767
Revises: d91550d42a11
Create Date: 2023-04-08 01:07:21.445128

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf0848efe767'
down_revision = 'd91550d42a11'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('jornadas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('jornada_actual', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('jornadas')
    # ### end Alembic commands ###
