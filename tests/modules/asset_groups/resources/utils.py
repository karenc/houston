# -*- coding: utf-8 -*-
"""
Asset_group resources utils
-------------
"""
import json
import shutil
import os
import config
from unittest import mock

from tests import utils as test_utils
from tests import TEST_ASSET_GROUP_UUID, TEST_EMPTY_ASSET_GROUP_UUID

PATH = '/api/v1/asset_groups/'


class TestCreationData(object):
    def __init__(self, transaction_id, populate_default=True):

        if not populate_default:
            self.content = {}
        else:
            self.content = {
                'description': 'This is a test asset_group, please ignore',
                'uploadType': 'form',
                'speciesDetectionModel': [
                    'None',
                ],
                'transactionId': transaction_id,
                'sightings': [
                    {
                        'startTime': '2000-01-01T01:01:01Z',
                        # Yes, that really is a location, it's a village in Wiltshire https://en.wikipedia.org/wiki/Tiddleywink
                        'locationId': 'Tiddleywink',
                        'encounters': [{}],
                    },
                ],
            }

    def add_filename(self, sighting, filename):
        if 'assetReferences' not in self.content['sightings'][sighting]:
            self.content['sightings'][sighting]['assetReferences'] = []
        self.content['sightings'][sighting]['assetReferences'].append(filename)

    def add_sighting(self, location):
        self.content['sightings'].append(
            {
                'locationId': location,
                'startTime': '2000-01-01T01:01:01Z',
                'assetReferences': [],
                'encounters': [],
            }
        )

    def add_encounter(self, sighting):
        self.content['sightings'][sighting]['encounters'].append({})

    def set_field(self, field, value):
        self.content[field] = value

    def remove_field(self, field):
        del self.content[field]

    def set_sighting_field(self, sighting, field, value):
        self.content['sightings'][sighting][field] = value

    def set_encounter_field(self, sighting, encounter, field, value):
        self.content['sightings'][sighting]['encounters'][encounter][field] = value

    def remove_encounter_field(self, sighting, encounter, field):
        del self.content['sightings'][sighting]['encounters'][encounter][field]

    def get(self):
        return self.content


def create_asset_group(
    flask_app_client, user, data, expected_status_code=200, expected_error=''
):
    from app.modules.asset_groups.tasks import sage_detection

    # Call sage_detection in the foreground by skipping "delay"
    with mock.patch(
        'app.modules.asset_groups.tasks.sage_detection.delay', side_effect=sage_detection
    ):
        if user:
            with flask_app_client.login(user, auth_scopes=('asset_groups:write',)):
                response = flask_app_client.post(
                    '%s' % PATH,
                    content_type='application/json',
                    data=json.dumps(data),
                )
        else:
            response = flask_app_client.post(
                '%s' % PATH,
                content_type='application/json',
                data=json.dumps(data),
            )

    if expected_status_code == 200:
        test_utils.validate_dict_response(
            response, 200, {'guid', 'description', 'major_type'}
        )
    elif 400 <= expected_status_code < 500:
        test_utils.validate_dict_response(
            response, expected_status_code, {'status', 'message'}
        )
        assert response.json['message'] == expected_error, response.json['message']
    else:
        test_utils.validate_dict_response(
            response, expected_status_code, {'status', 'message'}
        )
    return response


# As for method above but simulate a successful response from Sage and do some minimal validation
def create_asset_group_sim_sage(
    flask_app, flask_app_client, user, data, expected_status_code=200, expected_error=''
):
    # Simulate a valid response from Sage but don't actually send the request to Sage
    with mock.patch.object(
        flask_app.acm,
        'request_passthrough_result',
        return_value={'success': True},
    ) as detection_started:

        resp = create_asset_group(
            flask_app_client, user, data, expected_status_code, expected_error
        )
        passed_args = detection_started.call_args[0]
        try:
            assert passed_args[:-2] == ('job.detect_request', 'post')
            params = passed_args[-2]['params']
            assert set(params.keys()) >= {
                'endpoint',
                'jobid',
                'callback_url',
                'image_uuid_list',
                'input',
            }
        except Exception:
            # Calling code cannot clear up the asset group as the resp is not passed if any of the assertions fail
            # meaning that all subsequent tests would fail.
            if 'guid' in resp.json:
                delete_asset_group(flask_app_client, user, resp.json['guid'])
            raise
        return resp


# Helper as many bulk uploads use a common set of files
def create_bulk_tus_transaction(test_root):
    import tests.extensions.tus.utils as tus_utils

    transaction_id, test_filename = tus_utils.prep_tus_dir(test_root)
    tus_utils.prep_tus_dir(test_root, filename='coelacanth.png')
    tus_utils.prep_tus_dir(test_root, filename='fluke.jpg')
    tus_utils.prep_tus_dir(test_root, filename='phoenix.jpg')
    return transaction_id, test_filename


def get_bulk_creation_data(transaction_id, test_filename):
    data = TestCreationData(transaction_id)
    data.add_filename(0, test_filename)
    data.add_encounter(0)
    data.add_filename(0, 'fluke.jpg')
    data.add_sighting('Hogpits Bottom')
    data.add_encounter(1)
    data.add_filename(1, 'coelacanth.png')
    data.add_encounter(1)
    data.add_filename(1, 'phoenix.jpg')
    data.set_field('uploadType', 'bulk')
    return data


# Create a default valid Sage detection response (to allow for the test to corrupt it accordingly)
def build_sage_detection_response(asset_group_guid, job_uuid):
    from app.modules.asset_groups.models import AssetGroup
    import uuid

    asset_group = AssetGroup.query.get(asset_group_guid)

    # Generate the response back from Sage
    sage_resp = {
        'response': {
            'jobid': f'{str(job_uuid)}',
            'json_result': {
                'has_assignments': False,
                'image_uuid_list': [],
                'results_list': [],
                'score_list': [
                    0.0,
                ],
            },
            'status': 'completed',
        },
        'status': {
            'cache': -1,
            'code': 200,
            'message': {},
            'success': True,
        },
    }
    base_result = [
        {
            'class': 'whale_orca+fin_dorsal',
            'confidence': 0.7909,
            'height': 820,
            'id': 947505,
            'interest': False,
            'left': 140,
            'multiple': False,
            'quality': None,
            'species': 'whale_orca+fin_dorsal',
            'theta': 0.0,
            'top': 0,
            'uuid': '23b9ac5a-9a52-473a-a4dd-6a1f4f255dbc',
            'viewpoint': 'left',
            'width': 1063,
            'xtl': 140,
            'ytl': 0,
        }
    ]

    import copy

    for asset in asset_group.assets:
        sage_resp['response']['json_result']['image_uuid_list'].append(str(asset.guid))
        # Give each annotation a new UUID
        new_result = copy.deepcopy(base_result)
        new_result[0]['uuid'] = str(uuid.uuid4())
        sage_resp['response']['json_result']['results_list'].append(new_result)
    return sage_resp


def send_sage_detection_response(
    flask_app_client,
    user,
    asset_group_sighting_guid,
    job_guid,
    data,
    expected_status_code=200,
):
    with flask_app_client.login(user, auth_scopes=('asset_group_sightings:write',)):
        response = flask_app_client.post(
            f'{PATH}sighting/{asset_group_sighting_guid}/sage_detected/{job_guid}',
            content_type='application/json',
            data=json.dumps(data),
        )
    if expected_status_code == 200:
        assert response.status_code == expected_status_code
    else:
        test_utils.validate_dict_response(
            response, expected_status_code, {'status', 'message'}
        )
    return response


def commit_asset_group_sighting(
    flask_app_client,
    user,
    asset_group_sighting_guid,
    expected_status_code=200,
):
    with flask_app_client.login(user, auth_scopes=('asset_group_sightings:write',)):
        response = flask_app_client.post(
            f'{PATH}sighting/{asset_group_sighting_guid}/commit',
            content_type='application/json',
        )

    if expected_status_code == 200:
        test_utils.validate_dict_response(response, 200, {'guid'})
    else:
        test_utils.validate_dict_response(
            response, expected_status_code, {'status', 'message'}
        )
    return response


def create_asset_group_with_annotation(
    flask_app_client, db, user, transaction_id, test_filename
):
    data = TestCreationData(transaction_id)
    data.add_filename(0, test_filename)
    response = create_asset_group(flask_app_client, user, data.get())
    asset_group_uuid = response.json['guid']
    asset_group_sighting_guid = response.json['asset_group_sightings'][0]['guid']
    asset_uuid = response.json['assets'][0]['guid']
    annot_uuid = patch_in_dummy_annotation(
        flask_app_client, db, user, asset_group_sighting_guid, asset_uuid
    )
    return asset_group_uuid, asset_group_sighting_guid, annot_uuid


# Many tests require a committed assetgroup with one sighting, use this helper
def create_and_commit_asset_group(
    flask_app_client, db, user, transaction_id, test_filename
):
    (
        asset_group_uuid,
        asset_group_sighting_uuid,
        annot_uuid,
    ) = create_asset_group_with_annotation(
        flask_app_client, db, user, transaction_id, test_filename
    )

    response = commit_asset_group_sighting(
        flask_app_client, user, asset_group_sighting_uuid
    )

    sighting_uuid = response.json['guid']
    return asset_group_uuid, sighting_uuid, annot_uuid


def patch_asset_group(
    flask_app_client, user, asset_group_guid, data, expected_status_code=200
):
    with flask_app_client.login(user, auth_scopes=('asset_groups:write',)):
        response = flask_app_client.patch(
            '%s%s' % (PATH, asset_group_guid),
            content_type='application/json',
            data=json.dumps(data),
        )

    if expected_status_code == 200:
        test_utils.validate_dict_response(
            response, 200, {'guid', 'description', 'major_type'}
        )
    else:
        test_utils.validate_dict_response(
            response, expected_status_code, {'status', 'message'}
        )
    return response


def read_asset_group(flask_app_client, user, asset_group_guid, expected_status_code=200):
    if user:
        with flask_app_client.login(user, auth_scopes=('asset_groups:read',)):
            response = flask_app_client.get('%s%s' % (PATH, asset_group_guid))
    else:
        response = flask_app_client.get('%s%s' % (PATH, asset_group_guid))
    if expected_status_code == 200:
        test_utils.validate_dict_response(
            response, 200, {'guid', 'description', 'major_type'}
        )
    else:
        test_utils.validate_dict_response(
            response, expected_status_code, {'status', 'message'}
        )
    return response


def read_all_asset_groups(flask_app_client, user, expected_status_code=200):
    with flask_app_client.login(user, auth_scopes=('asset_groups:read',)):
        response = flask_app_client.get(PATH)

    if expected_status_code == 200:
        test_utils.validate_list_response(response, 200)
    else:
        test_utils.validate_dict_response(
            response, expected_status_code, {'status', 'message'}
        )
    return response


def delete_asset_group(
    flask_app_client, user, asset_group_guid, expected_status_code=204
):
    from app.modules.asset_groups.models import AssetGroup
    from app.modules.asset_groups.tasks import delete_remote

    with mock.patch('app.modules.asset_groups.tasks') as tasks:
        # Do delete_remote in the foreground immediately instead of using a
        # celery worker in the background
        tasks.delete_remote.delay.side_effect = lambda *args, **kwargs: delete_remote(
            *args, **kwargs
        )
        with flask_app_client.login(user, auth_scopes=('asset_groups:write',)):
            response = flask_app_client.delete('%s%s' % (PATH, asset_group_guid))

    if expected_status_code == 204:
        assert response.status_code == 204
        assert not AssetGroup.is_on_remote(asset_group_guid)
    else:
        test_utils.validate_dict_response(
            response, expected_status_code, {'status', 'message'}
        )


def patch_asset_group_sighting(
    flask_app_client,
    user,
    patch_path,
    data,
    expected_status_code=200,
    expected_resp='',
):
    with flask_app_client.login(user, auth_scopes=('asset_group_sightings:write',)):
        response = flask_app_client.patch(
            f'{PATH}sighting/{patch_path}',
            content_type='application/json',
            data=json.dumps(data),
        )

    if expected_status_code == 200:
        test_utils.validate_dict_response(response, 200, {'guid', 'stage', 'config'})
    elif expected_status_code == 400:
        test_utils.validate_dict_response(
            response, expected_status_code, {'status', 'message', 'passed_message'}
        )
        assert response.json['passed_message'] == expected_resp
    else:
        test_utils.validate_dict_response(
            response, expected_status_code, {'status', 'message'}
        )
    return response


def read_asset_group_sighting(
    flask_app_client, user, asset_group_sighting_guid, expected_status_code=200
):
    if user:
        with flask_app_client.login(user, auth_scopes=('asset_group_sightings:read',)):
            response = flask_app_client.get(f'{PATH}sighting/{asset_group_sighting_guid}')
    else:
        response = flask_app_client.get(f'{PATH}sighting/{asset_group_sighting_guid}')
    if expected_status_code == 200:
        test_utils.validate_dict_response(
            response, 200, {'guid', 'stage', 'config', 'completion', 'assets'}
        )
    else:
        test_utils.validate_dict_response(
            response, expected_status_code, {'status', 'message'}
        )
    return response


def simulate_detection_response(
    flask_app_client, user, path, data, expected_status_code=200
):
    with flask_app_client.login(user, auth_scopes=('asset_group_sightings:write',)):
        response = flask_app_client.post(
            f'{PATH}{path}',
            content_type='application/json',
            data=json.dumps(data),
        )

    if expected_status_code == 200:
        test_utils.validate_dict_response(response, 200, {})
    else:
        test_utils.validate_dict_response(
            response, expected_status_code, {'status', 'message'}
        )
    return response


# Helper as used across multiple tests
def patch_in_dummy_annotation(
    flask_app_client, db, user, asset_group_sighting_uuid, asset_uuid, encounter_num=0
):
    from app.modules.assets.models import Asset
    from app.modules.annotations.models import Annotation
    import uuid

    asset = Asset.find(asset_uuid)
    assert asset

    # Create a dummy annotation for this Sighting
    new_annot = Annotation(
        guid=uuid.uuid4(),
        asset=asset,
        ia_class='none',
        bounds={'rect': [45, 5, 78, 3], 'theta': 4.8},
    )
    with db.session.begin(subtransactions=True):
        db.session.add(new_annot)

    # Patch it in
    group_sighting = read_asset_group_sighting(
        flask_app_client, user, asset_group_sighting_uuid
    )
    encounter_guid = group_sighting.json['config']['encounters'][encounter_num]['guid']

    patch_data = [test_utils.patch_replace_op('annotations', [str(new_annot.guid)])]
    patch_asset_group_sighting(
        flask_app_client,
        user,
        f'{asset_group_sighting_uuid}/encounter/{encounter_guid}',
        patch_data,
    )
    return new_annot.guid


# multiple tests clone a asset_group, do something with it and clean it up. Make sure this always happens using a
# class with a cleanup method to be called if any assertions fail
class CloneAssetGroup(object):
    def __init__(self, client, owner, guid, force_clone):
        from app.modules.asset_groups.models import AssetGroup

        self.asset_group = None
        self.guid = guid

        # Allow the option of forced cloning, this could raise an exception if the assertion fails
        # but this does not need to be in any try/except/finally construct as no resources are allocated yet
        if force_clone:
            database_path = config.TestingConfig.ASSET_GROUP_DATABASE_PATH
            asset_group_path = os.path.join(database_path, str(guid))

            if os.path.exists(asset_group_path):
                shutil.rmtree(asset_group_path)
            assert not os.path.exists(asset_group_path)

        url = f'{PATH}{guid}'
        with client.login(owner, auth_scopes=('asset_groups:read',)):
            self.response = client.get(url)

        # only store the asset_group if the clone worked
        if self.response.status_code == 200:
            self.asset_group = AssetGroup.query.get(self.response.json['guid'])

        elif self.response.status_code in (428, 403):
            # 428 Precondition Required
            # 403 Forbidden
            with client.login(owner, auth_scopes=('asset_groups:write',)):
                self.response = client.post(url)

            # only store the asset_group if the clone worked
            if self.response.status_code == 200:
                self.asset_group = AssetGroup.query.get(self.response.json['guid'])

        else:
            assert (
                False
            ), f'url={url} status_code={self.response.status_code} data={self.response.data}'

    def remove_files(self):
        database_path = config.TestingConfig.ASSET_GROUP_DATABASE_PATH
        asset_group_path = os.path.join(database_path, str(self.guid))
        if os.path.exists(asset_group_path):
            shutil.rmtree(asset_group_path)

    def cleanup(self):
        # Restore original state if not one of the asset group fixtures
        if str(self.guid) not in (TEST_ASSET_GROUP_UUID, TEST_EMPTY_ASSET_GROUP_UUID):
            if self.asset_group is not None:
                self.asset_group.delete()
                self.asset_group = None
            self.remove_files()


# Clone the asset_group
def clone_asset_group(
    client,
    owner,
    guid,
    force_clone=False,
    expect_failure=False,
):
    clone = CloneAssetGroup(client, owner, guid, force_clone)

    if not expect_failure:
        assert clone.response.status_code == 200, clone.response.data
    return clone
