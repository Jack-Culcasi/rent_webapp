"""Booking/Contatacts relationship created

Revision ID: eb7ec4b2edfd
Revises: 3f5cbf2c36b9
Create Date: 2024-01-19 02:27:25.345281

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb7ec4b2edfd'
down_revision = '3f5cbf2c36b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.add_column(sa.Column('contact_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('booking_contacts_id', 'contacts', ['contact_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.drop_constraint('booking_contacts_id', type_='foreignkey')
        batch_op.drop_column('contact_id')

    # ### end Alembic commands ###