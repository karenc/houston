# -*- coding: utf-8 -*-
"""empty message

Revision ID: 973184c68d5e
Revises: 88244eed06d0
Create Date: 2022-01-04 20:51:52.814904

"""
from alembic import op
import sqlalchemy as sa

import app
import app.extensions


# revision identifiers, used by Alembic.
revision = '973184c68d5e'
down_revision = '88244eed06d0'


def upgrade():
    """
    Upgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'relationship',
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('guid', app.extensions.GUID(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('guid', name=op.f('pk_relationship')),
    )
    with op.batch_alter_table('relationship', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_relationship_end_date'), ['end_date'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_relationship_start_date'), ['start_date'], unique=False
        )

    op.create_table(
        'relationship_individual_member',
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('viewed', sa.DateTime(), nullable=False),
        sa.Column('guid', app.extensions.GUID(), nullable=False),
        sa.Column('relationship_guid', app.extensions.GUID(), nullable=True),
        sa.Column('individual_guid', app.extensions.GUID(), nullable=True),
        sa.Column('individual_role', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ['individual_guid'],
            ['individual.guid'],
            name=op.f('fk_relationship_individual_member_individual_guid_individual'),
        ),
        sa.ForeignKeyConstraint(
            ['relationship_guid'],
            ['relationship.guid'],
            name=op.f('fk_relationship_individual_member_relationship_guid_relationship'),
        ),
        sa.PrimaryKeyConstraint('guid', name=op.f('pk_relationship_individual_member')),
    )
    with op.batch_alter_table('relationship_individual_member', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_relationship_individual_member_created'),
            ['created'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_relationship_individual_member_updated'),
            ['updated'],
            unique=False,
        )

    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('relationship_individual_member', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_relationship_individual_member_updated'))
        batch_op.drop_index(batch_op.f('ix_relationship_individual_member_created'))

    op.drop_table('relationship_individual_member')
    with op.batch_alter_table('relationship', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_relationship_start_date'))
        batch_op.drop_index(batch_op.f('ix_relationship_end_date'))

    op.drop_table('relationship')
    # ### end Alembic commands ###
