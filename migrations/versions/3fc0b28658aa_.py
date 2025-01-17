# -*- coding: utf-8 -*-
"""empty message

Revision ID: 3fc0b28658aa
Revises: 804d984e9dd4
Create Date: 2022-01-25 09:09:17.621655

"""
from alembic import op
import sqlalchemy as sa

import app
import app.extensions
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '3fc0b28658aa'
down_revision = '804d984e9dd4'


def upgrade():
    """
    Upgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    major_type_postgres = postgresql.ENUM(
        'filesystem',
        'archive',
        'service',
        'test',
        'unknown',
        'error',
        'reject',
        name='gitstoremajortype',
        create_type=False,
    )
    major_type_sa = sa.Enum(
        'filesystem',
        'archive',
        'service',
        'test',
        'unknown',
        'error',
        'reject',
        name='gitstoremajortype',
    )
    major_type = major_type_sa.with_variant(major_type_postgres, 'postgresql')
    major_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'git_store',
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('viewed', sa.DateTime(), nullable=False),
        sa.Column('guid', app.extensions.GUID(), nullable=False),
        sa.Column('git_store_type', sa.String(length=32), nullable=True),
        sa.Column('major_type', major_type, autoincrement=False, nullable=False),
        sa.Column('owner_guid', app.extensions.GUID(), nullable=False),
        sa.Column('submitter_guid', app.extensions.GUID(), nullable=True),
        sa.Column('commit', sa.String(length=40), nullable=True),
        sa.Column('commit_mime_whitelist_guid', app.extensions.GUID(), nullable=True),
        sa.Column('commit_houston_api_version', sa.String(), nullable=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('config', app.extensions.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ['owner_guid'], ['user.guid'], name=op.f('fk_git_store_owner_guid_user')
        ),
        sa.ForeignKeyConstraint(
            ['submitter_guid'],
            ['user.guid'],
            name=op.f('fk_git_store_submitter_guid_user'),
        ),
        sa.PrimaryKeyConstraint('guid', name=op.f('pk_git_store')),
        sa.UniqueConstraint('commit', name=op.f('uq_git_store_commit')),
    )
    with op.batch_alter_table('git_store', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_git_store_commit_houston_api_version'),
            ['commit_houston_api_version'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_git_store_commit_mime_whitelist_guid'),
            ['commit_mime_whitelist_guid'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_git_store_created'), ['created'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_git_store_major_type'), ['major_type'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_git_store_owner_guid'), ['owner_guid'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_git_store_submitter_guid'), ['submitter_guid'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_git_store_updated'), ['updated'], unique=False
        )

    op.create_table(
        'mission_collection',
        sa.Column('guid', app.extensions.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['guid'],
            ['git_store.guid'],
            name=op.f('fk_mission_collection_guid_git_store'),
        ),
        sa.PrimaryKeyConstraint('guid', name=op.f('pk_mission_collection')),
    )
    with op.batch_alter_table('mission_collection', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('mission_guid', app.extensions.GUID(), nullable=False)
        )
        batch_op.create_index(
            batch_op.f('ix_mission_collection_mission_guid'),
            ['mission_guid'],
            unique=False,
        )
        batch_op.create_foreign_key(
            batch_op.f('fk_mission_collection_mission_guid_mission'),
            'mission',
            ['mission_guid'],
            ['guid'],
        )

    op.create_table(
        'mission_task',
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('viewed', sa.DateTime(), nullable=False),
        sa.Column('guid', app.extensions.GUID(), nullable=False),
        sa.Column('title', sa.String(length=50), nullable=False),
        sa.Column(
            'type',
            sa.Enum('placeholder', name='missiontasktypes'),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column('owner_guid', app.extensions.GUID(), nullable=True),
        sa.Column('mission_guid', app.extensions.GUID(), nullable=True),
        sa.Column('notes', sa.UnicodeText(), nullable=True),
        sa.ForeignKeyConstraint(
            ['mission_guid'],
            ['mission.guid'],
            name=op.f('fk_mission_task_mission_guid_mission'),
        ),
        sa.ForeignKeyConstraint(
            ['owner_guid'], ['user.guid'], name=op.f('fk_mission_task_owner_guid_user')
        ),
        sa.PrimaryKeyConstraint('guid', name=op.f('pk_mission_task')),
    )
    with op.batch_alter_table('mission_task', schema=None) as batch_op:
        batch_op.alter_column(
            'mission_guid', existing_type=app.extensions.GUID(), nullable=False
        )
        batch_op.create_index(
            batch_op.f('ix_mission_task_created'), ['created'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_mission_task_mission_guid'), ['mission_guid'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_mission_task_owner_guid'), ['owner_guid'], unique=False
        )
        batch_op.create_index(
            batch_op.f('ix_mission_task_updated'), ['updated'], unique=False
        )
        batch_op.create_unique_constraint(
            batch_op.f('uq_mission_task_mission_guid'), ['mission_guid', 'title']
        )

    op.create_table(
        'mission_task_asset_participation',
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('viewed', sa.DateTime(), nullable=False),
        sa.Column('mission_task_guid', app.extensions.GUID(), nullable=False),
        sa.Column('asset_guid', app.extensions.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['asset_guid'],
            ['asset.guid'],
            name=op.f('fk_mission_task_asset_participation_asset_guid_asset'),
        ),
        sa.ForeignKeyConstraint(
            ['mission_task_guid'],
            ['mission_task.guid'],
            name=op.f(
                'fk_mission_task_asset_participation_mission_task_guid_mission_task'
            ),
        ),
        sa.PrimaryKeyConstraint(
            'mission_task_guid',
            'asset_guid',
            name=op.f('pk_mission_task_asset_participation'),
        ),
    )
    with op.batch_alter_table(
        'mission_task_asset_participation', schema=None
    ) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_mission_task_asset_participation_created'),
            ['created'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_mission_task_asset_participation_updated'),
            ['updated'],
            unique=False,
        )

    op.create_table(
        'mission_task_user_assignment',
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('viewed', sa.DateTime(), nullable=False),
        sa.Column('mission_task_guid', app.extensions.GUID(), nullable=False),
        sa.Column('user_guid', app.extensions.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['mission_task_guid'],
            ['mission_task.guid'],
            name=op.f('fk_mission_task_user_assignment_mission_task_guid_mission_task'),
        ),
        sa.ForeignKeyConstraint(
            ['user_guid'],
            ['user.guid'],
            name=op.f('fk_mission_task_user_assignment_user_guid_user'),
        ),
        sa.PrimaryKeyConstraint(
            'mission_task_guid', 'user_guid', name=op.f('pk_mission_task_user_assignment')
        ),
    )
    with op.batch_alter_table('mission_task_user_assignment', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_mission_task_user_assignment_created'),
            ['created'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_mission_task_user_assignment_updated'),
            ['updated'],
            unique=False,
        )

    op.create_table(
        'mission_task_annotation_participation',
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('updated', sa.DateTime(), nullable=False),
        sa.Column('viewed', sa.DateTime(), nullable=False),
        sa.Column('mission_task_guid', app.extensions.GUID(), nullable=False),
        sa.Column('annotation_guid', app.extensions.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ['annotation_guid'],
            ['annotation.guid'],
            name=op.f(
                'fk_mission_task_annotation_participation_annotation_guid_annotation'
            ),
        ),
        sa.ForeignKeyConstraint(
            ['mission_task_guid'],
            ['mission_task.guid'],
            name=op.f(
                'fk_mission_task_annotation_participation_mission_task_guid_mission_task'
            ),
        ),
        sa.PrimaryKeyConstraint(
            'mission_task_guid',
            'annotation_guid',
            name=op.f('pk_mission_task_annotation_participation'),
        ),
    )
    with op.batch_alter_table(
        'mission_task_annotation_participation', schema=None
    ) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_mission_task_annotation_participation_created'),
            ['created'],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f('ix_mission_task_annotation_participation_updated'),
            ['updated'],
            unique=False,
        )

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_index('ix_task_created')
        batch_op.drop_index('ix_task_mission_guid')
        batch_op.drop_index('ix_task_owner_guid')
        batch_op.drop_index('ix_task_updated')

    with op.batch_alter_table('task_annotation_participation', schema=None) as batch_op:
        batch_op.drop_constraint(
            'fk_task_annotation_participation_task_guid_task', type_='foreignkey'
        )

    with op.batch_alter_table('task_user_assignment', schema=None) as batch_op:
        batch_op.drop_constraint(
            'fk_task_user_assignment_task_guid_task', type_='foreignkey'
        )

    with op.batch_alter_table('task_asset_participation', schema=None) as batch_op:
        batch_op.drop_constraint(
            'fk_task_asset_participation_task_guid_task', type_='foreignkey'
        )

    op.drop_table('task')
    with op.batch_alter_table('task_annotation_participation', schema=None) as batch_op:
        batch_op.drop_index('ix_task_annotation_participation_created')
        batch_op.drop_index('ix_task_annotation_participation_updated')

    op.drop_table('task_annotation_participation')
    with op.batch_alter_table('task_asset_participation', schema=None) as batch_op:
        batch_op.drop_index('ix_task_asset_participation_created')
        batch_op.drop_index('ix_task_asset_participation_updated')

    op.drop_table('task_asset_participation')
    with op.batch_alter_table('task_user_assignment', schema=None) as batch_op:
        batch_op.drop_index('ix_task_user_assignment_created')
        batch_op.drop_index('ix_task_user_assignment_updated')

    op.drop_table('task_user_assignment')
    with op.batch_alter_table('asset', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('git_store_guid', app.extensions.GUID(), nullable=False)
        )
        batch_op.drop_index('ix_asset_asset_group_guid')
        batch_op.create_index(
            batch_op.f('ix_asset_git_store_guid'), ['git_store_guid'], unique=False
        )
        batch_op.drop_constraint(
            'fk_asset_asset_group_guid_asset_group', type_='foreignkey'
        )
        batch_op.create_foreign_key(
            batch_op.f('fk_asset_git_store_guid_git_store'),
            'git_store',
            ['git_store_guid'],
            ['guid'],
            ondelete='CASCADE',
        )
        batch_op.drop_column('asset_group_guid')

    with op.batch_alter_table('asset_group', schema=None) as batch_op:
        batch_op.drop_index('ix_asset_group_commit_houston_api_version')
        batch_op.drop_index('ix_asset_group_commit_mime_whitelist_guid')
        batch_op.drop_index('ix_asset_group_created')
        batch_op.drop_index('ix_asset_group_major_type')
        batch_op.drop_index('ix_asset_group_owner_guid')
        batch_op.drop_index('ix_asset_group_submitter_guid')
        batch_op.drop_index('ix_asset_group_updated')
        batch_op.drop_constraint('uq_asset_group_commit', type_='unique')
        batch_op.drop_constraint('fk_asset_group_owner_guid_user', type_='foreignkey')
        batch_op.drop_constraint('fk_asset_group_submitter_guid_user', type_='foreignkey')
        batch_op.create_foreign_key(
            batch_op.f('fk_asset_group_guid_git_store'), 'git_store', ['guid'], ['guid']
        )
        batch_op.drop_column('created')
        batch_op.drop_column('owner_guid')
        batch_op.drop_column('submitter_guid')
        batch_op.drop_column('updated')
        batch_op.drop_column('commit')
        batch_op.drop_column('viewed')
        batch_op.drop_column('config')
        batch_op.drop_column('commit_mime_whitelist_guid')
        batch_op.drop_column('commit_houston_api_version')
        batch_op.drop_column('description')

    try:
        with op.batch_alter_table('asset_group', schema=None) as batch_op:
            batch_op.drop_column('major_type')
            if 'sqlite' in op.get_bind().dialect.dialect_description:
                batch_op.drop_constraint('ck_asset_group_assetgroupmajortype')
    except Exception:
        op.execute('COMMIT')
        with op.batch_alter_table('asset_group', schema=None) as batch_op:
            batch_op.drop_column('major_type')

    with op.batch_alter_table('mission', schema=None) as batch_op:
        batch_op.alter_column(
            'owner_guid', existing_type=app.extensions.GUID(), nullable=True
        )
        batch_op.create_unique_constraint(batch_op.f('uq_mission_title'), ['title'])

    with op.batch_alter_table('mission_asset_participation', schema=None) as batch_op:
        batch_op.drop_index('ix_mission_asset_participation_created')
        batch_op.drop_index('ix_mission_asset_participation_updated')

    op.drop_table('mission_asset_participation')

    sa.Enum(name='assetgroupmajortype').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='tasktypes').drop(op.get_bind(), checkfirst=False)
    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    major_type_postgres = postgresql.ENUM(
        'filesystem',
        'archive',
        'service',
        'test',
        'unknown',
        'error',
        'reject',
        name='assetgroupmajortype',
        create_type=False,
    )
    major_type_sa = sa.Enum(
        'filesystem',
        'archive',
        'service',
        'test',
        'unknown',
        'error',
        'reject',
        name='assetgroupmajortype',
    )
    major_type = major_type_sa.with_variant(major_type_postgres, 'postgresql')
    major_type.create(op.get_bind(), checkfirst=True)

    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('mission', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_mission_title'), type_='unique')
        batch_op.alter_column(
            'owner_guid', existing_type=app.extensions.GUID(), nullable=False
        )

    op.create_table(
        'task',
        sa.Column('created', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column('updated', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column('viewed', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column('guid', app.extensions.GUID(), autoincrement=False, nullable=False),
        sa.Column('title', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
        sa.Column(
            'type',
            sa.Enum('placeholder', name='tasktypes'),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            'owner_guid', app.extensions.GUID(), autoincrement=False, nullable=True
        ),
        sa.Column(
            'mission_guid', app.extensions.GUID(), autoincrement=False, nullable=True
        ),
        sa.Column('notes', sa.TEXT(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ['mission_guid'], ['mission.guid'], name='fk_task_mission_guid_mission'
        ),
        sa.ForeignKeyConstraint(
            ['owner_guid'], ['user.guid'], name='fk_task_owner_guid_user'
        ),
        sa.PrimaryKeyConstraint('guid', name='pk_task'),
    )
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.create_index('ix_task_updated', ['updated'], unique=False)
        batch_op.create_index('ix_task_owner_guid', ['owner_guid'], unique=False)
        batch_op.create_index('ix_task_mission_guid', ['mission_guid'], unique=False)
        batch_op.create_index('ix_task_created', ['created'], unique=False)

    with op.batch_alter_table('asset_group', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'description', sa.VARCHAR(length=255), autoincrement=False, nullable=True
            )
        )
        batch_op.add_column(
            sa.Column(
                'commit_houston_api_version',
                sa.VARCHAR(),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                'commit_mime_whitelist_guid',
                app.extensions.GUID(),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                'config',
                sa.JSON(),
                autoincrement=False,
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column('viewed', sa.DateTime(), autoincrement=False, nullable=False)
        )
        batch_op.add_column(
            sa.Column('commit', sa.VARCHAR(length=40), autoincrement=False, nullable=True)
        )
        batch_op.add_column(
            sa.Column('updated', sa.DateTime(), autoincrement=False, nullable=False)
        )
        batch_op.add_column(
            sa.Column(
                'submitter_guid',
                app.extensions.GUID(),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column('major_type', major_type, autoincrement=False, nullable=False)
        )
        batch_op.add_column(
            sa.Column(
                'owner_guid', app.extensions.GUID(), autoincrement=False, nullable=False
            )
        )
        batch_op.add_column(
            sa.Column('created', sa.DateTime(), autoincrement=False, nullable=False)
        )
        batch_op.drop_constraint(
            batch_op.f('fk_asset_group_guid_git_store'), type_='foreignkey'
        )
        batch_op.create_foreign_key(
            'fk_asset_group_submitter_guid_user', 'user', ['submitter_guid'], ['guid']
        )
        batch_op.create_foreign_key(
            'fk_asset_group_owner_guid_user', 'user', ['owner_guid'], ['guid']
        )
        batch_op.create_unique_constraint('uq_asset_group_commit', ['commit'])
        batch_op.create_index('ix_asset_group_updated', ['updated'], unique=False)
        batch_op.create_index(
            'ix_asset_group_submitter_guid', ['submitter_guid'], unique=False
        )
        batch_op.create_index('ix_asset_group_owner_guid', ['owner_guid'], unique=False)
        batch_op.create_index('ix_asset_group_major_type', ['major_type'], unique=False)
        batch_op.create_index('ix_asset_group_created', ['created'], unique=False)
        batch_op.create_index(
            'ix_asset_group_commit_mime_whitelist_guid',
            ['commit_mime_whitelist_guid'],
            unique=False,
        )
        batch_op.create_index(
            'ix_asset_group_commit_houston_api_version',
            ['commit_houston_api_version'],
            unique=False,
        )

    with op.batch_alter_table('asset_group', schema=None) as batch_op:
        if 'sqlite' in op.get_bind().dialect.dialect_description:
            batch_op.drop_constraint('assetgroupmajortype')

    with op.batch_alter_table('asset', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'asset_group_guid',
                app.extensions.GUID(),
                autoincrement=False,
                nullable=False,
            )
        )
        batch_op.drop_constraint(
            batch_op.f('fk_asset_git_store_guid_git_store'), type_='foreignkey'
        )
        batch_op.create_foreign_key(
            'fk_asset_asset_group_guid_asset_group',
            'asset_group',
            ['asset_group_guid'],
            ['guid'],
            ondelete='CASCADE',
        )
        batch_op.drop_index(batch_op.f('ix_asset_git_store_guid'))
        batch_op.create_index(
            'ix_asset_asset_group_guid', ['asset_group_guid'], unique=False
        )
        batch_op.drop_column('git_store_guid')

    op.create_table(
        'task_user_assignment',
        sa.Column('created', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column('updated', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column('viewed', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column(
            'task_guid', app.extensions.GUID(), autoincrement=False, nullable=False
        ),
        sa.Column(
            'user_guid', app.extensions.GUID(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['task_guid'], ['task.guid'], name='fk_task_user_assignment_task_guid_task'
        ),
        sa.ForeignKeyConstraint(
            ['user_guid'], ['user.guid'], name='fk_task_user_assignment_user_guid_user'
        ),
        sa.PrimaryKeyConstraint('task_guid', 'user_guid', name='pk_task_user_assignment'),
    )
    with op.batch_alter_table('task_user_assignment', schema=None) as batch_op:
        batch_op.create_index(
            'ix_task_user_assignment_updated', ['updated'], unique=False
        )
        batch_op.create_index(
            'ix_task_user_assignment_created', ['created'], unique=False
        )

    op.create_table(
        'task_asset_participation',
        sa.Column('created', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column('updated', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column('viewed', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column(
            'task_guid', app.extensions.GUID(), autoincrement=False, nullable=False
        ),
        sa.Column(
            'asset_guid', app.extensions.GUID(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['asset_guid'],
            ['asset.guid'],
            name='fk_task_asset_participation_asset_guid_asset',
        ),
        sa.ForeignKeyConstraint(
            ['task_guid'],
            ['task.guid'],
            name='fk_task_asset_participation_task_guid_task',
        ),
        sa.PrimaryKeyConstraint(
            'task_guid', 'asset_guid', name='pk_task_asset_participation'
        ),
    )
    with op.batch_alter_table('task_asset_participation', schema=None) as batch_op:
        batch_op.create_index(
            'ix_task_asset_participation_updated', ['updated'], unique=False
        )
        batch_op.create_index(
            'ix_task_asset_participation_created', ['created'], unique=False
        )

    op.create_table(
        'task_annotation_participation',
        sa.Column('created', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column('updated', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column('viewed', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column(
            'task_guid', app.extensions.GUID(), autoincrement=False, nullable=False
        ),
        sa.Column(
            'annotation_guid', app.extensions.GUID(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['annotation_guid'],
            ['annotation.guid'],
            name='fk_task_annotation_participation_annotation_guid_annotation',
        ),
        sa.ForeignKeyConstraint(
            ['task_guid'],
            ['task.guid'],
            name='fk_task_annotation_participation_task_guid_task',
        ),
        sa.PrimaryKeyConstraint(
            'task_guid', 'annotation_guid', name='pk_task_annotation_participation'
        ),
    )
    with op.batch_alter_table('task_annotation_participation', schema=None) as batch_op:
        batch_op.create_index(
            'ix_task_annotation_participation_updated', ['updated'], unique=False
        )
        batch_op.create_index(
            'ix_task_annotation_participation_created', ['created'], unique=False
        )

    with op.batch_alter_table(
        'mission_task_annotation_participation', schema=None
    ) as batch_op:
        batch_op.drop_index(
            batch_op.f('ix_mission_task_annotation_participation_updated')
        )
        batch_op.drop_index(
            batch_op.f('ix_mission_task_annotation_participation_created')
        )

    op.drop_table('mission_task_annotation_participation')
    with op.batch_alter_table('mission_task_user_assignment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mission_task_user_assignment_updated'))
        batch_op.drop_index(batch_op.f('ix_mission_task_user_assignment_created'))

    op.drop_table('mission_task_user_assignment')
    with op.batch_alter_table(
        'mission_task_asset_participation', schema=None
    ) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mission_task_asset_participation_updated'))
        batch_op.drop_index(batch_op.f('ix_mission_task_asset_participation_created'))

    op.drop_table('mission_task_asset_participation')
    with op.batch_alter_table('mission_task', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_mission_task_updated'))
        batch_op.drop_index(batch_op.f('ix_mission_task_owner_guid'))
        batch_op.drop_index(batch_op.f('ix_mission_task_mission_guid'))
        batch_op.drop_index(batch_op.f('ix_mission_task_created'))
        batch_op.drop_constraint(
            batch_op.f('uq_mission_task_mission_guid'), type_='unique'
        )
        batch_op.alter_column(
            'mission_guid', existing_type=app.extensions.GUID(), nullable=True
        )

    with op.batch_alter_table('mission_collection', schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f('fk_mission_collection_mission_guid_mission'), type_='foreignkey'
        )
        batch_op.drop_index(batch_op.f('ix_mission_collection_mission_guid'))
        batch_op.drop_column('mission_guid')

    op.drop_table('mission_task')
    op.drop_table('mission_collection')

    with op.batch_alter_table('git_store', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_git_store_updated'))
        batch_op.drop_index(batch_op.f('ix_git_store_submitter_guid'))
        batch_op.drop_index(batch_op.f('ix_git_store_owner_guid'))
        batch_op.drop_index(batch_op.f('ix_git_store_major_type'))
        batch_op.drop_index(batch_op.f('ix_git_store_created'))
        batch_op.drop_index(batch_op.f('ix_git_store_commit_mime_whitelist_guid'))
        batch_op.drop_index(batch_op.f('ix_git_store_commit_houston_api_version'))

    op.drop_table('git_store')

    op.create_table(
        'mission_asset_participation',
        sa.Column('created', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column('updated', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column('viewed', sa.DateTime(), autoincrement=False, nullable=False),
        sa.Column(
            'mission_guid', app.extensions.GUID(), autoincrement=False, nullable=False
        ),
        sa.Column(
            'asset_guid', app.extensions.GUID(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['asset_guid'],
            ['asset.guid'],
            name='fk_mission_asset_participation_asset_guid_asset',
        ),
        sa.ForeignKeyConstraint(
            ['mission_guid'],
            ['mission.guid'],
            name='fk_mission_asset_participation_mission_guid_mission',
        ),
        sa.PrimaryKeyConstraint(
            'mission_guid', 'asset_guid', name='pk_mission_asset_participation'
        ),
    )
    with op.batch_alter_table('mission_asset_participation', schema=None) as batch_op:
        batch_op.create_index(
            'ix_mission_asset_participation_updated', ['updated'], unique=False
        )
        batch_op.create_index(
            'ix_mission_asset_participation_created', ['created'], unique=False
        )

    sa.Enum(name='gitstoremajortype').drop(op.get_bind(), checkfirst=False)
    sa.Enum(name='missiontasktypes').drop(op.get_bind(), checkfirst=False)
    # ### end Alembic commands ###
