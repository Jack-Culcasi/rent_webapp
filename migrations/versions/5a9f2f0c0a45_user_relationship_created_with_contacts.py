"""User relationship created with Contacts

Revision ID: 5a9f2f0c0a45
Revises: d0208b9aed0b
Create Date: 2024-01-10 17:03:52.484736

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5a9f2f0c0a45'
down_revision = 'd0208b9aed0b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contacts', schema=None) as batch_op:
        batch_op.alter_column('full_name',
               existing_type=sa.VARCHAR(length=8),
               type_=sa.String(length=128),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contacts', schema=None) as batch_op:
        batch_op.alter_column('full_name',
               existing_type=sa.String(length=128),
               type_=sa.VARCHAR(length=8),
               existing_nullable=True)

    # ### end Alembic commands ###
