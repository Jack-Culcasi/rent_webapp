"""empty message

Revision ID: 07dfa2cd4b87
Revises: 3f58530e8f3f
Create Date: 2023-11-17 17:00:06.096661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07dfa2cd4b87'
down_revision = '3f58530e8f3f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('car', schema=None) as batch_op:
        batch_op.drop_constraint('_plate_uc', type_='unique')
        batch_op.drop_index('ix_car_plate')
        batch_op.create_index(batch_op.f('ix_car_plate'), ['plate'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('car', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_car_plate'))
        batch_op.create_index('ix_car_plate', ['plate'], unique=False)
        batch_op.create_unique_constraint('_plate_uc', ['plate'])

    # ### end Alembic commands ###
