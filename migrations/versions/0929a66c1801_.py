"""empty message

Revision ID: 0929a66c1801
Revises: 4f26a551ddc0
Create Date: 2024-06-12 00:42:09.646312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0929a66c1801'
down_revision = '4f26a551ddc0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('clickup_user_id', sa.String(length=80), nullable=False))
        batch_op.create_unique_constraint(None, ['clickup_user_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('clickup_user_id')

    # ### end Alembic commands ###
