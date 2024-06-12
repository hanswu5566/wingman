"""empty message

Revision ID: 4f26a551ddc0
Revises: 
Create Date: 2024-06-10 23:48:12.689078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f26a551ddc0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slack_user_id', sa.String(length=80), nullable=False),
    sa.Column('slack_team_id', sa.String(length=80), nullable=False),
    sa.Column('slack_name', sa.String(length=120), nullable=False),
    sa.Column('clickup_token', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('clickup_token'),
    sa.UniqueConstraint('slack_user_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###