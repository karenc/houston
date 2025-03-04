# -*- coding: utf-8 -*-
"""empty message

Revision ID: 8bea1f7d2e44
Revises: 5c2ffe7143c9
Create Date: 2021-05-20 08:08:01.140046

"""
from alembic import op
import sqlalchemy as sa

import app
import app.extensions

from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision = '8bea1f7d2e44'
down_revision = '5c2ffe7143c9'


def upgrade():
    """
    Upgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('asset_group_job', schema=None) as batch_op:
        batch_op.drop_index('ix_asset_group_job_owner_guid')

    op.drop_table('asset_group_job')
    with op.batch_alter_table('asset_group', schema=None) as batch_op:
        batch_op.add_column(sa.Column('config', sa.JSON(), nullable=True))
        batch_op.drop_column('meta')

    with op.batch_alter_table('asset_group_sighting', schema=None) as batch_op:
        batch_op.add_column(sa.Column('config', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('jobs', sa.JSON(), nullable=True))
        batch_op.drop_column('meta')

    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('asset_group_sighting', schema=None) as batch_op:
        batch_op.add_column(sa.Column('meta', sqlite.JSON(), nullable=True))
        batch_op.drop_column('jobs')
        batch_op.drop_column('config')

    with op.batch_alter_table('asset_group', schema=None) as batch_op:
        batch_op.add_column(sa.Column('meta', sqlite.JSON(), nullable=True))
        batch_op.drop_column('config')

    op.create_table(
        'asset_group_job',
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('viewed', sa.DateTime(), nullable=False),
        sa.Column('guid', app.extensions.GUID(), nullable=False),
        sa.Column('owner_guid', app.extensions.GUID(), nullable=False),
        sa.Column('jobId', app.extensions.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['owner_guid'],
            ['asset_group_sighting.guid'],
            name=op.f('fk_asset_group_job_owner_guid_asset_group_sighting'),
        ),
        sa.PrimaryKeyConstraint('guid', name=op.f('pk_asset_group_job')),
    )
    with op.batch_alter_table('asset_group_job', schema=None) as batch_op:
        batch_op.create_index(
            'ix_asset_group_job_owner_guid', ['owner_guid'], unique=False
        )

    # ### end Alembic commands ###
