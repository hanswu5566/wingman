"""empty message

Revision ID: 84af18f14e0c
Revises: 
Create Date: 2024-07-25 01:01:08.666621

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '84af18f14e0c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contexts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slack_user_id', sa.String(length=80), nullable=False),
    sa.Column('last_clickup_dify_answer', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('contexts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_contexts_slack_user_id'), ['slack_user_id'], unique=True)

    op.create_table('targets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slack_user_id', sa.String(length=80), nullable=False),
    sa.Column('clickup_lists', postgresql.ARRAY(sa.String(length=80)), nullable=False),
    sa.Column('ios_teammates', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('web_teammates', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('android_teammates', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('backend_teammates', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('product_manager_teammates', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('engineering_manager_teammates', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('product_designer_teammates', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('targets', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_targets_slack_user_id'), ['slack_user_id'], unique=True)

    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('slack_user_id', sa.String(length=80), nullable=False),
    sa.Column('slack_team_id', sa.String(length=80), nullable=False),
    sa.Column('slack_user_name', sa.String(length=120), nullable=False),
    sa.Column('clickup_token', sa.String(length=120), nullable=True),
    sa.Column('clickup_user_id', sa.String(length=80), nullable=True),
    sa.Column('clickup_user_name', sa.String(length=120), nullable=True),
    sa.Column('clickup_team_id', sa.String(length=120), nullable=True),
    sa.Column('clickup_team_name', sa.String(length=120), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('clickup_team_id'),
    sa.UniqueConstraint('clickup_token'),
    sa.UniqueConstraint('clickup_user_id'),
    sa.UniqueConstraint('slack_team_id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_slack_user_id'), ['slack_user_id'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_slack_user_id'))

    op.drop_table('user')
    with op.batch_alter_table('targets', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_targets_slack_user_id'))

    op.drop_table('targets')
    with op.batch_alter_table('contexts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_contexts_slack_user_id'))

    op.drop_table('contexts')
    # ### end Alembic commands ###
