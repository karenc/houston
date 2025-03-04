# -*- coding: utf-8 -*-
"""empty message

Revision ID: 5c2ffe7143c9
Revises: 13e7f8e7bcf8
Create Date: 2021-05-18 10:54:07.907512

"""
from alembic import op
import sqlalchemy as sa

import app
import app.extensions


# revision identifiers, used by Alembic.
revision = '5c2ffe7143c9'
down_revision = '13e7f8e7bcf8'


def upgrade():
    """
    Upgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('asset_group', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('submitter_guid', app.extensions.GUID(), nullable=True)
        )
        batch_op.create_index(
            batch_op.f('ix_asset_group_submitter_guid'), ['submitter_guid'], unique=False
        )
        batch_op.create_foreign_key(
            batch_op.f('fk_asset_group_submitter_guid_user'),
            'user',
            ['submitter_guid'],
            ['guid'],
        )

    with op.batch_alter_table('asset_group_sighting', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('asset_group_guid', app.extensions.GUID(), nullable=False)
        )
        batch_op.add_column(sa.Column('meta', sa.JSON(), nullable=True))
        batch_op.drop_index('ix_asset_group_sighting_owner_guid')
        batch_op.create_index(
            batch_op.f('ix_asset_group_sighting_asset_group_guid'),
            ['asset_group_guid'],
            unique=False,
        )
        batch_op.drop_constraint(
            'fk_asset_group_sighting_owner_guid_asset_group', type_='foreignkey'
        )
        batch_op.create_foreign_key(
            batch_op.f('fk_asset_group_sighting_asset_group_guid_asset_group'),
            'asset_group',
            ['asset_group_guid'],
            ['guid'],
        )
        batch_op.drop_column('owner_guid')

    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('asset_group_sighting', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('owner_guid', app.extensions.GUID(), nullable=False)
        )
        batch_op.drop_constraint(
            batch_op.f('fk_asset_group_sighting_asset_group_guid_asset_group'),
            type_='foreignkey',
        )
        batch_op.create_foreign_key(
            'fk_asset_group_sighting_owner_guid_asset_group',
            'asset_group',
            ['owner_guid'],
            ['guid'],
        )
        batch_op.drop_index(batch_op.f('ix_asset_group_sighting_asset_group_guid'))
        batch_op.create_index(
            'ix_asset_group_sighting_owner_guid', ['owner_guid'], unique=False
        )
        batch_op.drop_column('meta')
        batch_op.drop_column('asset_group_guid')

    with op.batch_alter_table('asset_group', schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f('fk_asset_group_submitter_guid_user'), type_='foreignkey'
        )
        batch_op.drop_index(batch_op.f('ix_asset_group_submitter_guid'))
        batch_op.drop_column('submitter_guid')

    # ### end Alembic commands ###
