# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation
"""
RESTful API Encounters resources
--------------------------
"""

import logging

from flask_login import current_user  # NOQA
from flask_restx_patched import Resource
from flask_restx_patched._http import HTTPStatus
from flask import request, current_app

from app.extensions import db
from app.extensions.api import Namespace
from app.extensions.api.parameters import PaginationParameters
from app.modules.users import permissions
from app.modules.users.permissions.types import AccessOperation
from app.utils import HoustonException

from app.extensions.api import abort

from . import parameters, schemas
from .models import Encounter


log = logging.getLogger(__name__)  # pylint: disable=invalid-name
api = Namespace('encounters', description='Encounters')  # pylint: disable=invalid-name


@api.route('/')
class Encounters(Resource):
    """
    Manipulations with Encounters.
    """

    @api.permission_required(
        permissions.ModuleAccessPermission,
        kwargs_on_request=lambda kwargs: {
            'module': Encounter,
            'action': AccessOperation.READ,
        },
    )
    @api.login_required(oauth_scopes=['encounters:read'])
    @api.parameters(PaginationParameters())
    @api.response(schemas.BaseEncounterSchema(many=True))
    def get(self, args):
        """
        List of Encounter.

        Returns a list of Encounter starting from ``offset`` limited by ``limit``
        parameter.
        """
        return Encounter.query.offset(args['offset']).limit(args['limit'])


@api.route('/<uuid:encounter_guid>')
@api.response(
    code=HTTPStatus.NOT_FOUND,
    description='Encounter not found.',
)
@api.resolve_object_by_model(Encounter, 'encounter')
class EncounterByID(Resource):
    """
    Manipulations with a specific Encounter.
    """

    @api.permission_required(
        permissions.ObjectAccessPermission,
        kwargs_on_request=lambda kwargs: {
            'obj': kwargs['encounter'],
            'action': AccessOperation.READ,
        },
    )
    def get(self, encounter):
        """
        Get Encounter full details by ID.
        """

        # note: should probably _still_ check edm for: stale cache, deletion!
        #      user.edm_sync(version)

        response = current_app.edm.get_dict('encounter.data_complete', encounter.guid)
        if not isinstance(response, dict):  # some non-200 thing, incl 404
            return response

        return encounter.augment_edm_json(response['result'])

    @api.permission_required(
        permissions.ObjectAccessPermission,
        kwargs_on_request=lambda kwargs: {
            'obj': kwargs['encounter'],
            'action': AccessOperation.WRITE,
        },
    )
    @api.login_required(oauth_scopes=['encounters:write'])
    @api.parameters(parameters.PatchEncounterDetailsParameters())
    @api.response(code=HTTPStatus.CONFLICT)
    def patch(self, args, encounter):
        """
        Patch Encounter details by ID.
        """

        edm_args = [
            arg
            for arg in args
            if arg.get('path')
            in parameters.PatchEncounterDetailsParameters.PATH_CHOICES_EDM
        ]
        if edm_args and len(edm_args) != len(args):
            log.error(f'Mixed edm/houston patch called with args {args}')
            abort(400, 'Cannot mix EDM patch paths and houston patch paths')

        if not edm_args:
            context = api.commit_or_abort(
                db.session, default_error_message='Failed to update Encounter details.'
            )
            with context:
                parameters.PatchEncounterDetailsParameters.perform_patch(
                    args, obj=encounter
                )
                db.session.merge(encounter)
            # this mimics output format of edm-patching
            return {
                'id': str(encounter.guid),
                'version': encounter.version,
            }

        # must be edm patch
        log.debug(f'wanting to do edm patch on args={args}')
        try:
            result_data = current_app.edm.request_passthrough_result(
                'encounter.data',
                'patch',
                {'data': args},
                encounter.guid,
                request_headers=request.headers,
            )
        except HoustonException as ex:
            abort(
                ex.status_code,
                ex.message,
                error=ex.error,
                edm_status_code=ex.edm_status_code,
            )

        # edm patch was successful
        new_version = result_data.get('version', None)
        if new_version is not None:
            encounter.version = new_version
            context = api.commit_or_abort(
                db.session,
                default_error_message='Failed to update Encounter version.',
            )
            with context:
                db.session.merge(encounter)
        # rtn['_patchResults'] = rdata.get('patchResults', None)  # FIXME i think this gets lost cuz not part of results_data
        return result_data

    @api.permission_required(
        permissions.ObjectAccessPermission,
        kwargs_on_request=lambda kwargs: {
            'obj': kwargs['encounter'],
            'action': AccessOperation.DELETE,
        },
    )
    @api.login_required(oauth_scopes=['encounters:write'])
    @api.response(code=HTTPStatus.CONFLICT)
    @api.response(code=HTTPStatus.NO_CONTENT)
    def delete(self, encounter):
        """
        Delete a Encounter by ID.
        """
        # first try delete on edm
        response = encounter.delete_from_edm(current_app)
        response_data = None
        if response.ok:
            response_data = response.json()

        if not response.ok or not response_data.get('success', False):
            log.warning(
                'Encounter.delete %r failed: %r' % (encounter.guid, response_data)
            )
            abort(
                success=False, passed_message='Delete failed', message='Error', code=400
            )

        # if we get here, edm has deleted the encounter, now houston feather
        # TODO handle failure of feather deletion (when edm successful!)  out-of-sync == bad
        encounter.delete()
        return None
