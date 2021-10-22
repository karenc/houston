# -*- coding: utf-8 -*-
"""
Social Groups database models
--------------------
"""

import logging

from app.extensions import db, HoustonModel
from app.utils import HoustonException
import app.extensions.logging as AuditLog

import uuid

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class SocialGroupIndividualMembership(db.Model, HoustonModel):

    group_guid = db.Column(db.GUID, db.ForeignKey('social_group.guid'), primary_key=True)

    individual_guid = db.Column(
        db.GUID, db.ForeignKey('individual.guid'), primary_key=True
    )
    roles = db.Column(db.JSON, nullable=True)

    social_group = db.relationship(
        'SocialGroup', back_populates='members', order_by='SocialGroup.guid'
    )

    individual = db.relationship(
        'Individual', back_populates='social_groups', order_by='Individual.guid'
    )

    def __repr__(self):
        return (
            '<{class_name}('
            'group_guid={self.group_guid}, '
            'individual_guid={self.individual_guid}, '
            'roles={self.roles} '
            ')>'.format(class_name=self.__class__.__name__, self=self)
        )


class SocialGroup(db.Model, HoustonModel):
    """
    Social Groups database model.
    """

    guid = db.Column(
        db.GUID, default=uuid.uuid4, primary_key=True
    )  # pylint: disable=invalid-name
    name = db.Column(db.String(length=50), nullable=False)

    members = db.relationship(
        'SocialGroupIndividualMembership',
        back_populates='social_group',
        order_by='SocialGroupIndividualMembership.group_guid',
    )

    def __init__(self, members, name):
        self.name = name

        for member_guid in members:
            self.add_member(member_guid, members[member_guid])

    def __repr__(self):
        return (
            '<{class_name}('
            'guid={self.guid}, '
            "name='{self.name}'"
            ')>'.format(class_name=self.__class__.__name__, self=self)
        )

    @classmethod
    def site_settings_updated(cls):
        from app.modules.site_settings.models import SiteSetting

        permitted_role_data = SiteSetting.get_json('social_group_roles')
        all_groups = SocialGroup.query.all()
        for group in all_groups:
            current_roles_singular = {}
            for member in group.members:
                if not member.roles:
                    continue
                if not permitted_role_data:
                    member.roles = None
                    with db.session.begin(subtransactions=True):
                        db.session.merge(member)
                    continue

                for role in member.roles:
                    if role not in permitted_role_data.keys():
                        # That role not supported anymore
                        msg = f"member {member.individual_guid} lost role {role} as it's no longer supported"
                        AuditLog.audit_log_object(log, group, msg)
                        member.roles.remove(role)

                        # Ensure it's written to the DB
                        member.roles = member.roles
                        with db.session.begin(subtransactions=True):
                            db.session.merge(member)
                        continue

                    # if a role is now only singular in the group and we have multiple, all we can do is audit it
                    if permitted_role_data[role]['multipleInGroup']:
                        if current_roles_singular.get(role):
                            current_roles_singular[role] = False
                        else:
                            current_roles_singular[role] = True

                for role in current_roles_singular:
                    if not current_roles_singular[role]:
                        msg = f"WARNING: multiple members with {role}. Can't guess which to remove"
                        AuditLog.audit_log_object(log, group, msg)

    # This is for validating te site settings social group roles format, not the roles of an individual social group
    @classmethod
    def validate_roles(cls, roles_input):
        expected_fields = {'multipleInGroup'}
        if not isinstance(roles_input, dict):
            raise HoustonException(log, 'Role data needs to be a dictionary')
        for item in roles_input:
            if not isinstance(roles_input[item], dict):
                raise HoustonException(
                    log, 'Role data needs to be a dictionary of dictionaries'
                )

            if set(roles_input[item].keys()) != set(expected_fields):
                raise HoustonException(
                    log,
                    f'Role dictionary must have the following keys : {expected_fields}',
                )

    def get_member_data_as_json(self):
        individual_data = {}
        for member in self.members:
            individual_data[str(member.individual_guid)] = {'roles': member.roles}

        return individual_data

    def get_member(self, individual_guid):
        found_members = [
            member
            for member in self.members
            if str(member.individual_guid) == individual_guid
        ]
        return found_members[0] if len(found_members) else None

    def remove_member(self, individual_guid):
        ret_val = False
        # make sure it's a valid request
        member = self.get_member(individual_guid)
        if member:
            with db.session.begin(subtransactions=True):
                db.session.delete(member)
            ret_val = True
        return ret_val

    def add_member(self, individual_guid, data):
        from app.modules.individuals.models import Individual

        individual = Individual.query.get(individual_guid)
        assert individual
        membership = SocialGroupIndividualMembership(
            social_group=self,
            individual=individual,
            roles=data.get('roles'),
        )
        with db.session.begin(subtransactions=True):
            db.session.add(membership)

    def delete(self):
        AuditLog.delete_object(log, self)

        with db.session.begin(subtransactions=True):
            for member in self.members:
                db.session.delete(member)
            db.session.delete(self)
