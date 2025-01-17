# -*- coding: utf-8 -*-
"""empty message

Revision ID: 2d3ba401d0f0
Revises: 4b2d7014d79e
Create Date: 2021-08-20 13:09:29.168663

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d3ba401d0f0'
down_revision = '4b2d7014d79e'


def upgrade():
    """
    Upgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_read', sa.Boolean(), nullable=False))
        batch_op.drop_column('status')

    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'status', sa.VARCHAR(length=255), autoincrement=False, nullable=False
            )
        )
        batch_op.drop_column('is_read')

    # ### end Alembic commands ###
