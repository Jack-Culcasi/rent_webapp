"""Currency, unit and language column added to User

Revision ID: 910302c92d8c
Revises: f0a839fc555a
Create Date: 2024-02-02 17:04:06.196748

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '910302c92d8c'
down_revision = 'f0a839fc555a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('currency', sa.String(length=1), nullable=True))
        batch_op.add_column(sa.Column('measurement_unit', sa.String(length=5), nullable=True))
        batch_op.add_column(sa.Column('language', sa.String(length=2), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('language')
        batch_op.drop_column('measurement_unit')
        batch_op.drop_column('currency')

    # ### end Alembic commands ###
