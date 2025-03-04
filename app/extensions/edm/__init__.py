# -*- coding: utf-8 -*-
# pylint: disable=no-self-use
"""
Ecological Data Management (EDM) manager.

"""
import logging
from flask import current_app, request, session, render_template  # NOQA
from flask_login import current_user  # NOQA
from app.extensions import db
from app.extensions.restManager.RestManager import RestManager
from app.utils import HoustonException

import types
import tqdm
import keyword
import uuid
import sqlalchemy
import app.extensions.logging as AuditLog  # NOQA

from flask_restx_patched import is_extension_enabled

if not is_extension_enabled('edm'):
    raise RuntimeError('EDM is not enabled')


KEYWORD_SET = set(keyword.kwlist)

log = logging.getLogger(__name__)


class EDMManager(RestManager):
    """
        note the content of User in the 2nd item has stuff you can ignore. it also has the id as "uuid" (which is what it is internally, sigh).  also note it references Organizations !  we didnt touch on this on the call, but i think this should (must?) live with Users.  what we have in java is very lightweight anyway, so no loss to go away.   as you can see, user.organizations is an array of orgs, and (since it is many-to-many) you will see org.members is a list of Users.  easy peasy.  btw, by the time we got to Organizations, we did call the primary key id and make it a uuid.  "live and learn".  :confused:
    also!  the user.profileAsset is fabricated!  ben wanted something so i literally hardcoded a random choice (including empty) from a list of like 4 user faces. haha.  so you arent going crazy if you see this change per user.  and obviously in the future the contents of this will be more whatever we land on for final asset format.

        btw, as a bonus.  here is what an Organization is on wildbook[edm] ... they are hierarchical -- which i would argue we drop!!  it was fun for playing with, but i do not want to have to support that when security starts using these!!!  (no real world orgs use this currently anyway, not in any important way.)   other than that (and killing it off!) there are .members and .logoAsset.  boringly simple.
    https://nextgen.dev-wildbook.org/api/org.ecocean.Organization?id==%273b868b21-729f-46ca-933f-c4ecdf02e97d%27
    """

    NAME = 'EDM'
    ENDPOINT_PREFIX = 'api'

    # this is based on edm date of most recent commit (we must be at or greater than this)
    MIN_VERSION = '2022-02-02 12:34:56 -0700'

    # We use // as a shorthand for prefix
    # fmt: off
    ENDPOINTS = {
        'session': {
            'login': '//v0/login?content={"login":"%s","password":"%s"}',
        },
        'user': {
            'list': '//v0/org.ecocean.User/list',
            'data': '//v0/org.ecocean.User/%s',
            'data_complete': '//v0/org.ecocean.User/%s?detail-org.ecocean.User=max',
        },
        'encounter': {
            'list': '//v0/org.ecocean.Encounter/list',
            'data': '//v0/org.ecocean.Encounter/%s',
            'data_complete': '//v0/org.ecocean.Encounter/%s?detail-org.ecocean.Encounter=max',
        },
        'sighting': {
            'list': '//v0/org.ecocean.Occurrence/list',
            'data': '//v0/org.ecocean.Occurrence/%s',
            'data_complete': '//v0/org.ecocean.Occurrence/%s?detail-org.ecocean.Occurrence=max&detail-org.ecocean.Encounter=max',
        },
        'individual': {
            'list': '//v0/org.ecocean.MarkedIndividual/list',
            'data': '//v0/org.ecocean.MarkedIndividual/%s',
            'data_complete': '//v0/org.ecocean.MarkedIndividual/%s?detail-org.ecocean.MarkedIndividual=max',
            'merge': '//v0/merge',
        },
        'organization': {
            'list': '//v0/org.ecocean.Organization/list',
            'data': '//v0/org.ecocean.Organization/%s',
        },
        'collaboration': {
            'list': '//v0/org.ecocean.security.Collaboration/list',
        },
        'role': {
            'list': '//v0/org.ecocean.Role/list',
        },
        'passthrough': {
            'data': '',
        },
        'configuration': {
            'data': '//v0/configuration/%s',
            'init': '//v0/init?content=%s',
        },
        'configurationDefinition': {
            'data': '//v0/configurationDefinition/%s',
        },
        'version': {
            'dict': '/edm/json/git-info.json',
        }
    }
    # fmt: on

    def __init__(self, pre_initialize=False, *args, **kwargs):
        super(EDMManager, self).__init__(pre_initialize, *args, **kwargs)

    def version_check(self):
        edm_version = self.get_dict('version.dict', None)
        if edm_version is None or 'date' not in edm_version:
            log.error('could not determine EDM version')
            return False
        if edm_version['date'] >= self.MIN_VERSION:
            log.debug(
                f"EDM version check passed: edm_version={edm_version['date']}  >=  min_version={self.MIN_VERSION}"
            )
            return True
        log.error(
            f"EDM version check FAILED: edm_version={edm_version['date']}  <  min_version={self.MIN_VERSION}"
        )
        return False

    def initialize_edm_admin_user(self, email, password):
        import json

        edm_data = {
            'admin_user_initialized': {
                'email': email,
                'password': password,
                'username': email,
            }
        }
        target = 'default'  # TODO will we create admin on other targets?
        data = current_app.edm.get_dict(
            'configuration.init',
            json.dumps(edm_data),
            target=target,
        )
        if data.get('success', False):
            edm_auth = current_app.config.get('EDM_AUTHENTICATIONS', {})
            edm_auth[target] = {'username': email, 'password': password}
            from app.extensions.config.models import HoustonConfig

            HoustonConfig.set('EDM_AUTHENTICATIONS', edm_auth)
            log.info(
                f'Success creating startup (edm) admin user via API: {email}. (saved credentials in HoustonConfig)'
            )
            return True
        else:
            log.warning(
                f'Failed creating startup (edm) admin user {email} via API. (response {data})'
            )
            return False

    # The edm API returns a success and a result, this processes it to raise an exception on any
    # error and provide validated parsed output for further processing
    def request_passthrough_parsed(
        self,
        tag,
        method,
        passthrough_kwargs,
        args=None,
        target='default',
        request_headers=None,
    ):

        # here we handle special headers needed specifically for EDM, which come via incoming request_headers
        if request_headers is not None:
            headers = passthrough_kwargs.get('headers', {})
            headers['x-allow-delete-cascade-individual'] = request_headers.get(
                'x-allow-delete-cascade-individual', 'false'
            )
            headers['x-allow-delete-cascade-sighting'] = request_headers.get(
                'x-allow-delete-cascade-sighting', 'false'
            )
            passthrough_kwargs['headers'] = headers
        response = self.request_passthrough(tag, method, passthrough_kwargs, args, target)
        response_data = None
        result_data = None
        try:
            response_data = response.json()
        except Exception:
            pass
        if response.ok and response_data is not None:
            result_data = response_data.get('result', None)

        if (
            not response.ok
            or not response_data.get('success', False)
            or response.status_code != 200
        ):
            status_code = response.status_code
            if status_code > 600:
                status_code = 400  # flask doesnt like us to use "invalid" codes. :(

            message = {'unknown error'}
            error = None

            if response_data is not None and 'message' in response_data:
                message = response_data['message']
            if response_data is not None and 'errorFields' in response_data:
                error = response_data['errorFields']

            raise HoustonException(
                log,
                f'{tag} {method} failed {message} {response.status_code}',
                AuditLog.AuditType.BackEndFault,
                status_code=status_code,
                message=message,
                error=error,
                edm_status_code=response.status_code,
            )

        return response, response_data, result_data

    # Provides the same validation and exception raising as above but just returns the result
    def request_passthrough_result(
        self, tag, method, passthrough_kwargs, args=None, request_headers=None
    ):
        response, response_data, result = self.request_passthrough_parsed(
            tag,
            method,
            passthrough_kwargs,
            args,
            request_headers=request_headers,
        )
        return result


class EDMObjectMixin(object):
    @classmethod
    def edm_sync_all(cls, verbose=True, refresh=False):
        edm_items = current_app.edm.get_list('%s.list' % (cls.EDM_NAME,))

        if verbose:
            log.info(
                'Checking %d EDM %ss against local cache...'
                % (len(edm_items), cls.EDM_NAME)
            )

        new_items = []
        stale_items = []
        for guid in tqdm.tqdm(edm_items):
            item_version = edm_items[guid]
            version = item_version.get('version', None)
            assert version is not None

            model_obj, is_new = cls.ensure_edm_obj(guid)
            if is_new:
                new_items.append(model_obj)

            if model_obj.version != version or refresh:
                stale_items.append((model_obj, version))

        if verbose:
            log.info(f'Added {len(new_items)} new {cls.EDM_NAME}s')
            log.info(f'Updating {len(stale_items)} stale {cls.EDM_NAME}s using EDM...')

        updated_items = []
        failed_items = []
        for model_obj, version in tqdm.tqdm(stale_items):
            try:
                model_obj._sync_item(model_obj.guid, version)
                updated_items.append(model_obj)
            except sqlalchemy.exc.IntegrityError:
                log.exception(f'Error updating {cls.EDM_NAME} {model_obj}')

                failed_items.append(model_obj)

        return edm_items, new_items, updated_items, failed_items

    def _process_edm_attribute(self, data, edm_attribute):
        edm_attribute = edm_attribute.strip()
        edm_attribute = edm_attribute.strip('.')
        edm_attribute_list = edm_attribute.split('.')

        num_components = len(edm_attribute_list)

        if num_components == 0:
            raise AttributeError()

        edm_attribute_ = edm_attribute_list[0]
        edm_attribute_ = edm_attribute_.strip()
        data_ = getattr(data, edm_attribute_)

        if num_components == 1:
            return data_

        edm_attribute_list_ = edm_attribute_list[1:]
        edm_attribute_ = '.'.join(edm_attribute_list_)

        return self._process_edm_attribute(data_, edm_attribute_)

    def _process_edm_data(self, data, claimed_version):

        unmapped_attributes = list(
            set(sorted(data._fields)) - set(self.EDM_ATTRIBUTE_MAPPING)
        )
        if len(unmapped_attributes) > 0:
            log.warning('Unmapped attributes: %r' % (unmapped_attributes,))

        found_version = None
        for edm_attribute in self.EDM_ATTRIBUTE_MAPPING:
            try:
                edm_value = self._process_edm_attribute(data, edm_attribute)

                attribute = self.EDM_ATTRIBUTE_MAPPING[edm_attribute]
                if attribute is None:
                    log.warning(
                        'Ignoring mapping for EDM attribute %r' % (edm_attribute,)
                    )
                    continue

                if edm_attribute in self.EDM_LOG_ATTRIBUTES:
                    log.info(
                        'Syncing edm data for %r = %r'
                        % (
                            edm_attribute,
                            edm_value,
                        )
                    )

                assert hasattr(self, attribute), 'attribute not found'
                attribute_ = getattr(self, attribute)
                if isinstance(attribute_, (types.MethodType,)):
                    attribute_(edm_value)
                else:
                    setattr(self, attribute, edm_value)
                    if edm_attribute == self.EDM_VERSION_ATTRIBUTE:
                        found_version = edm_value
            except AttributeError:
                AuditLog.backend_fault(
                    log, f'Could not find EDM attribute {edm_attribute}'
                )

            except KeyError:
                AuditLog.backend_fault(
                    log, f'Could not find EDM attribute {edm_attribute}'
                )

        if found_version is None:
            self.version = claimed_version
        else:
            self.version = found_version

        with db.session.begin():
            db.session.merge(self)

        if found_version is None:
            log.info('Updating to claimed version %r' % (claimed_version,))
        else:
            log.info('Updating to found version %r' % (found_version,))

    def _sync_item(self, guid, version):
        response = current_app.edm.get_data_item(guid, '%s.data' % (self.EDM_NAME,))

        assert response.success
        data = response.result

        assert uuid.UUID(data.id) == guid

        self._process_edm_data(data, version)


def init_app(app, **kwargs):
    # pylint: disable=unused-argument
    """
    API extension initialization point.
    """
    app.edm = EDMManager()
