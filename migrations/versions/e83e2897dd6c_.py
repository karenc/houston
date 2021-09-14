"""empty message

Revision ID: e83e2897dd6c
Revises: caf961b9ac34
Create Date: 2021-09-10 17:03:14.518622

"""

# revision identifiers, used by Alembic.
revision = 'e83e2897dd6c'
down_revision = 'caf961b9ac34'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

import app
import app.extensions



def upgrade():
    """
    Upgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('annotation', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_annotation_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_annotation_updated'), ['updated'], unique=False)

    with op.batch_alter_table('annotation_keywords', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_annotation_keywords_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_annotation_keywords_updated'), ['updated'], unique=False)

    with op.batch_alter_table('asset', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_asset_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_asset_updated'), ['updated'], unique=False)

    with op.batch_alter_table('asset_group', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_asset_group_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_asset_group_updated'), ['updated'], unique=False)

    with op.batch_alter_table('asset_group_sighting', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_asset_group_sighting_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_asset_group_sighting_updated'), ['updated'], unique=False)

    with op.batch_alter_table('audit_log', schema=None) as batch_op:
        batch_op.add_column(sa.Column('duration', sa.Float(), nullable=True))
        batch_op.drop_column('user_email')
        batch_op.drop_column('message')
        batch_op.add_column(sa.Column('user_email', sa.String(), nullable=False))
        batch_op.add_column(sa.Column('message', sa.String(), nullable=True))
        batch_op.create_index(batch_op.f('ix_audit_log_audit_type'), ['audit_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_audit_log_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_audit_log_item_guid'), ['item_guid'], unique=False)
        batch_op.create_index(batch_op.f('ix_audit_log_message'), ['message'], unique=False)
        batch_op.create_index(batch_op.f('ix_audit_log_module_name'), ['module_name'], unique=False)
        batch_op.create_index(batch_op.f('ix_audit_log_updated'), ['updated'], unique=False)

    with op.batch_alter_table('code', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_code_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_code_updated'), ['updated'], unique=False)

    with op.batch_alter_table('collaboration', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_collaboration_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_collaboration_updated'), ['updated'], unique=False)

    with op.batch_alter_table('collaboration_user_associations', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_collaboration_user_associations_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_collaboration_user_associations_updated'), ['updated'], unique=False)

    with op.batch_alter_table('encounter', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_encounter_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_encounter_updated'), ['updated'], unique=False)

    with op.batch_alter_table('file_upload', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_file_upload_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_file_upload_updated'), ['updated'], unique=False)

    with op.batch_alter_table('houston_config', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_houston_config_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_houston_config_updated'), ['updated'], unique=False)

    with op.batch_alter_table('individual', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_individual_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_individual_updated'), ['updated'], unique=False)

    with op.batch_alter_table('keyword', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_keyword_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_keyword_updated'), ['updated'], unique=False)

    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_notification_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_notification_updated'), ['updated'], unique=False)

    with op.batch_alter_table('organization', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_organization_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_organization_updated'), ['updated'], unique=False)

    with op.batch_alter_table('organization_user_membership_enrollment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_organization_user_membership_enrollment_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_organization_user_membership_enrollment_updated'), ['updated'], unique=False)

    with op.batch_alter_table('organization_user_moderator_enrollment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_organization_user_moderator_enrollment_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_organization_user_moderator_enrollment_updated'), ['updated'], unique=False)

    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_project_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_project_updated'), ['updated'], unique=False)

    with op.batch_alter_table('project_encounter', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_project_encounter_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_project_encounter_updated'), ['updated'], unique=False)

    with op.batch_alter_table('project_user_membership_enrollment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_project_user_membership_enrollment_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_project_user_membership_enrollment_updated'), ['updated'], unique=False)

    with op.batch_alter_table('sighting', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_sighting_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_sighting_updated'), ['updated'], unique=False)

    with op.batch_alter_table('sighting_assets', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_sighting_assets_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_sighting_assets_updated'), ['updated'], unique=False)

    with op.batch_alter_table('site_setting', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_site_setting_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_site_setting_updated'), ['updated'], unique=False)

    with op.batch_alter_table('system_notification_preferences', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_system_notification_preferences_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_system_notification_preferences_updated'), ['updated'], unique=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_updated'), ['updated'], unique=False)

    with op.batch_alter_table('user_notification_preferences', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_notification_preferences_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_notification_preferences_updated'), ['updated'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade Semantic Description:
        ENTER DESCRIPTION HERE
    """
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_notification_preferences', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_notification_preferences_updated'))
        batch_op.drop_index(batch_op.f('ix_user_notification_preferences_created'))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_updated'))
        batch_op.drop_index(batch_op.f('ix_user_created'))

    with op.batch_alter_table('system_notification_preferences', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_system_notification_preferences_updated'))
        batch_op.drop_index(batch_op.f('ix_system_notification_preferences_created'))

    with op.batch_alter_table('site_setting', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_site_setting_updated'))
        batch_op.drop_index(batch_op.f('ix_site_setting_created'))

    with op.batch_alter_table('sighting_assets', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_sighting_assets_updated'))
        batch_op.drop_index(batch_op.f('ix_sighting_assets_created'))

    with op.batch_alter_table('sighting', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_sighting_updated'))
        batch_op.drop_index(batch_op.f('ix_sighting_created'))

    with op.batch_alter_table('project_user_membership_enrollment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_project_user_membership_enrollment_updated'))
        batch_op.drop_index(batch_op.f('ix_project_user_membership_enrollment_created'))

    with op.batch_alter_table('project_encounter', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_project_encounter_updated'))
        batch_op.drop_index(batch_op.f('ix_project_encounter_created'))

    with op.batch_alter_table('project', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_project_updated'))
        batch_op.drop_index(batch_op.f('ix_project_created'))

    with op.batch_alter_table('organization_user_moderator_enrollment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_organization_user_moderator_enrollment_updated'))
        batch_op.drop_index(batch_op.f('ix_organization_user_moderator_enrollment_created'))

    with op.batch_alter_table('organization_user_membership_enrollment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_organization_user_membership_enrollment_updated'))
        batch_op.drop_index(batch_op.f('ix_organization_user_membership_enrollment_created'))

    with op.batch_alter_table('organization', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_organization_updated'))
        batch_op.drop_index(batch_op.f('ix_organization_created'))

    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_notification_updated'))
        batch_op.drop_index(batch_op.f('ix_notification_created'))

    with op.batch_alter_table('keyword', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_keyword_updated'))
        batch_op.drop_index(batch_op.f('ix_keyword_created'))

    with op.batch_alter_table('individual', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_individual_updated'))
        batch_op.drop_index(batch_op.f('ix_individual_created'))

    with op.batch_alter_table('houston_config', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_houston_config_updated'))
        batch_op.drop_index(batch_op.f('ix_houston_config_created'))

    with op.batch_alter_table('file_upload', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_file_upload_updated'))
        batch_op.drop_index(batch_op.f('ix_file_upload_created'))

    with op.batch_alter_table('encounter', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_encounter_updated'))
        batch_op.drop_index(batch_op.f('ix_encounter_created'))

    with op.batch_alter_table('collaboration_user_associations', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_collaboration_user_associations_updated'))
        batch_op.drop_index(batch_op.f('ix_collaboration_user_associations_created'))

    with op.batch_alter_table('collaboration', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_collaboration_updated'))
        batch_op.drop_index(batch_op.f('ix_collaboration_created'))

    with op.batch_alter_table('code', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_code_updated'))
        batch_op.drop_index(batch_op.f('ix_code_created'))

    with op.batch_alter_table('audit_log', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_audit_log_updated'))
        batch_op.drop_index(batch_op.f('ix_audit_log_module_name'))
        batch_op.drop_index(batch_op.f('ix_audit_log_message'))
        batch_op.drop_index(batch_op.f('ix_audit_log_item_guid'))
        batch_op.drop_index(batch_op.f('ix_audit_log_created'))
        batch_op.drop_index(batch_op.f('ix_audit_log_audit_type'))
        batch_op.drop_column('duration')
        batch_op.drop_column('user_email')
        batch_op.drop_column('message')
        batch_op.add_column(sa.Column('user_email', sa.String(), nullable=False))
        batch_op.add_column(sa.Column('message', sa.String(), nullable=False))

    with op.batch_alter_table('asset_group_sighting', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_asset_group_sighting_updated'))
        batch_op.drop_index(batch_op.f('ix_asset_group_sighting_created'))

    with op.batch_alter_table('asset_group', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_asset_group_updated'))
        batch_op.drop_index(batch_op.f('ix_asset_group_created'))

    with op.batch_alter_table('asset', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_asset_updated'))
        batch_op.drop_index(batch_op.f('ix_asset_created'))

    with op.batch_alter_table('annotation_keywords', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_annotation_keywords_updated'))
        batch_op.drop_index(batch_op.f('ix_annotation_keywords_created'))

    with op.batch_alter_table('annotation', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_annotation_updated'))
        batch_op.drop_index(batch_op.f('ix_annotation_created'))

    # ### end Alembic commands ###
