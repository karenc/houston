# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
import pytest
from tests import utils as test_utils
import logging

log = logging.getLogger(__name__)


@pytest.mark.skipif(
    test_utils.module_unavailable('individuals', 'encounters', 'sightings'),
    reason='Individuals module disabled',
)
def test_get_conflicts(
    db,
    flask_app_client,
    researcher_1,
    researcher_2,
    request,
    test_root,
):
    from app.modules.individuals.models import Individual
    from tests.modules.individuals.resources import utils as individual_utils

    # make sure anon gets 401
    res = individual_utils.merge_conflicts(
        flask_app_client, None, [], expected_status_code=401
    )

    # set up 2 similar individuals
    individual1_uuids = individual_utils.create_individual_and_sighting(
        flask_app_client,
        researcher_1,
        request,
        test_root,
    )
    individual2_uuids = individual_utils.create_individual_and_sighting(
        flask_app_client,
        researcher_1,
        request,
        test_root,
    )
    individual1_guid = individual1_uuids['individual']
    individual2_guid = individual2_uuids['individual']

    # bunk individual data
    res = individual_utils.merge_conflicts(
        flask_app_client,
        researcher_2,
        [],
        expected_status_code=500,
    )

    # unknown individual guid
    res = individual_utils.merge_conflicts(
        flask_app_client,
        researcher_2,
        [individual1_guid, '0c898eb4-b913-4080-8dc5-5caefa8a1c82'],
        expected_status_code=404,
    )

    # no access to researcher_2
    res = individual_utils.merge_conflicts(
        flask_app_client,
        researcher_2,
        [individual1_guid, individual2_guid],
        expected_status_code=403,
    )

    # ok, with no conflicts
    res = individual_utils.merge_conflicts(
        flask_app_client,
        researcher_1,
        [individual1_guid, individual2_guid],
    )
    assert not len(res)

    # now one with sex set
    indiv_data = {'sex': 'male'}
    individual3_uuids = individual_utils.create_individual_and_sighting(
        flask_app_client,
        researcher_1,
        request,
        test_root,
        individual_data=indiv_data,
    )
    individual3_guid = individual3_uuids['individual']
    res = individual_utils.merge_conflicts(
        flask_app_client,
        researcher_1,
        [individual1_guid, individual3_guid],
    )
    assert res == {'sex': True}

    # add some names with a common context
    individual1 = Individual.query.get(individual1_guid)
    individual2 = Individual.query.get(individual2_guid)
    assert individual1
    assert individual2
    shared_context = 'test-context'
    individual1.add_name(shared_context, 'name1', researcher_1)
    individual2.add_name(shared_context, 'name2', researcher_1)
    individual2.add_name('a different context', 'nameX', researcher_1)
    res = individual_utils.merge_conflicts(
        flask_app_client,
        researcher_1,
        [individual1_guid, individual2_guid],
    )
    assert 'name_contexts' in res
    assert len(res['name_contexts']) == 1
    assert res['name_contexts'][0] == shared_context


@pytest.mark.skipif(
    test_utils.module_unavailable('individuals', 'encounters', 'sightings'),
    reason='Individuals module disabled',
)
def test_overrides(
    db,
    flask_app_client,
    researcher_1,
    researcher_2,
    request,
    test_root,
):
    from tests.modules.individuals.resources import utils as individual_utils

    indiv1_data = {'sex': 'male'}
    individual1_uuids = individual_utils.create_individual_and_sighting(
        flask_app_client,
        researcher_1,
        request,
        test_root,
        individual_data=indiv1_data,
    )
    indiv2_data = {'sex': 'female'}
    individual2_uuids = individual_utils.create_individual_and_sighting(
        flask_app_client,
        researcher_1,
        request,
        test_root,
        individual_data=indiv2_data,
    )
    individual1_guid = individual1_uuids['individual']
    individual2_guid = individual2_uuids['individual']

    data = [individual2_guid]
    res = individual_utils.merge_individuals(
        flask_app_client,
        researcher_1,
        individual1_guid,
        data_in=data,
    )
    assert res
    assert res.get('targetId') == individual1_guid
    assert res.get('targetSex') == 'male'

    # indiv1 and indiv3 male, but override merge with female
    indiv3_data = {'sex': 'male'}
    individual3_uuids = individual_utils.create_individual_and_sighting(
        flask_app_client,
        researcher_1,
        request,
        test_root,
        individual_data=indiv3_data,
    )
    individual3_guid = individual3_uuids['individual']
    data = {
        'fromIndividualIds': [individual1_guid],
        'parameters': {
            'override': {'sex': 'female'},
        },
    }
    res = individual_utils.merge_individuals(
        flask_app_client,
        researcher_1,
        individual3_guid,
        data_in=data,
    )
    assert res
    assert res.get('targetId') == individual3_guid
    assert res.get('targetSex') == 'female'
