# -*- coding: utf-8 -*-
"""
Relationships database models
--------------------
"""

from app.extensions import HoustonModel, db
from datetime import datetime  # NOQA
import app.extensions.logging as AuditLog

import uuid

import logging

log = logging.getLogger(__name__)


class RelationshipIndividualMember(db.Model, HoustonModel):

    guid = db.Column(
        db.GUID, default=uuid.uuid4, primary_key=True
    )  # pylint: disable=invalid-name

    relationship_guid = db.Column(db.GUID, db.ForeignKey('relationship.guid'))
    relationship = db.relationship(
        'Relationship', backref=db.backref('individual_members')
    )

    individual_guid = db.Column(db.GUID, db.ForeignKey('individual.guid'))
    individual = db.relationship('Individual', backref=db.backref('relationships'))

    individual_role = db.Column(db.String, nullable=False)

    def __init__(self, individual, individual_role, **kwargs):
        self.individual = individual
        self.individual_role = individual_role
        self.individual_guid = individual.guid

    def delete(self):
        relationship = Relationship.query.get(self.relationship_guid)
        relationship.delete()


class Relationship(db.Model, HoustonModel):
    """
    Relationships database model.
    """

    guid = db.Column(
        db.GUID, default=uuid.uuid4, primary_key=True
    )  # pylint: disable=invalid-name

    start_date = db.Column(
        db.DateTime, index=True, default=datetime.utcnow, nullable=True
    )
    end_date = db.Column(db.DateTime, index=True, default=datetime.utcnow, nullable=True)

    type = db.Column(db.String, nullable=True)

    def __init__(
        self,
        individual_1_guid,
        individual_2_guid,
        individual_1_role,
        individual_2_role,
        **kwargs
    ):
        if (
            individual_1_guid
            and individual_2_guid
            and individual_1_role
            and individual_2_role
        ):

            from app.modules.individuals.models import Individual

            individual_1 = Individual.query.get(individual_1_guid)
            individual_2 = Individual.query.get(individual_2_guid)

            if individual_1 and individual_2:
                member_1 = RelationshipIndividualMember(individual_1, individual_1_role)
                member_2 = RelationshipIndividualMember(individual_2, individual_2_role)
                self.individual_members.append(member_1)
                self.individual_members.append(member_2)
            else:
                raise ValueError(
                    'One of the Individual guids used to attempt Relationship creation was invalid.'
                )
        else:
            raise ValueError('Relationship needs two individuals, each with a role.')

    def has_individual(self, individual_guid):
        if self._get_membership_for_guid(individual_guid):
            return True
        return False

    def get_relationship_role_for_individual(self, individual_guid):
        membership = self._get_membership_for_guid(individual_guid)
        if membership:
            for individual_member in self.individual_members:
                if str(individual_member.individual_guid) == individual_guid:
                    return individual_member.individual_role
        return None

    def _get_membership_for_guid(self, individual_guid):
        found_individual_members = [
            individual_member
            for individual_member in self.individual_members
            if str(individual_member.individual_guid) == individual_guid
        ]
        return found_individual_members[0]

    def __repr__(self):
        return (
            '<{class_name}('
            'guid={self.guid}, '
            'individual_member_1={self.individual_members[0].individual_guid}, '
            'individual_member_2={self.individual_members[1].individual_guid}, '
            ')>'.format(class_name=self.__class__.__name__, self=self)
        )

    def delete(self):
        AuditLog.delete_object(log, self)

        with db.session.begin(subtransactions=True):
            for individual_member in self.individual_members:
                db.session.delete(individual_member)
            db.session.delete(self)
