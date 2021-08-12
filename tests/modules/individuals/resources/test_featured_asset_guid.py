# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from tests.modules.sightings.resources import utils as sighting_utils
from tests.modules.asset_groups.resources import utils as asset_group_utils
from tests.modules.individuals.resources import utils as individual_utils
from tests.modules.annotations.resources import utils as annot_utils
from tests import utils


def test_patch_featured_asset_guid_on_individual(db, flask_app_client, researcher_1):

    # this test is a monster because it involves almost all of the major modules

    from app.modules.sightings.models import Sighting

    data_in = {
        'encounters': [{}],
        'startTime': '2000-01-01T01:01:01Z',
        'locationId': 'test',
    }

    response = sighting_utils.create_sighting(
        flask_app_client, researcher_1, data_in=data_in
    )

    from app.modules.encounters.models import Encounter

    response_json = response.json

    import logging

    log = logging.getLogger(__name__)
    log.warning('RETURNED ENC JSON: ' + str(response_json))

    assert response_json['result']['encounters']
    assert response_json['result']['encounters'][0]
    assert response_json['result']['encounters'][0]['id']

    guid = response_json['result']['encounters'][0]['id']

    enc = Encounter(
        guid=guid,
        owner_guid=researcher_1.guid,
    )

    sighting_id = response_json['result']['id']
    sighting = Sighting.query.get(sighting_id)
    assert sighting is not None

    new_asset_group = utils.generate_asset_group_instance(researcher_1)

    with db.session.begin():
        db.session.add(new_asset_group)

    new_asset_1 = utils.generate_asset_instance(new_asset_group.guid)
    new_asset_2 = utils.generate_asset_instance(new_asset_group.guid)

    with db.session.begin():
        db.session.add(new_asset_group)
        db.session.add(new_asset_1)
        db.session.add(new_asset_2)
        db.session.add(enc)

    sighting.add_asset(new_asset_1)

    individual_response = individual_utils.create_individual(
        flask_app_client, researcher_1, 200, {'encounters': [{'id': str(enc.guid)}]}
    )

    from app.modules.individuals.models import Individual

    individual = Individual.query.get(individual_response.json['result']['id'])

    assert individual is not None
    assert new_asset_1.guid is not None
    assert new_asset_2.guid is not None

    ann_resp_1 = annot_utils.create_annotation(
        flask_app_client,
        researcher_1,
        str(new_asset_1.guid),
        str(enc.guid),
    )
    ann_guid_1 = ann_resp_1.json['guid']

    ann_resp_2 = annot_utils.create_annotation(
        flask_app_client,
        researcher_1,
        str(new_asset_2.guid),
        str(enc.guid),
    )

    ann_guid_2 = ann_resp_2.json['guid']

    from app.modules.annotations.models import Annotation

    ann_1 = Annotation.query.get(ann_guid_1)
    ann_2 = Annotation.query.get(ann_guid_2)
    with db.session.begin():
        db.session.add(ann_1)
        db.session.add(ann_2)

    ann_1.encounter = enc
    ann_2.encounter = enc

    enc.annotations.append(ann_1)
    enc.annotations.append(ann_2)

    assert enc is Encounter.query.get(individual.encounters[0])

    assert ann_1 is not None
    assert ann_2 is not None
    assert ann_1.encounter is not None
    assert ann_2.encounter is not None
    assert len(enc.annotations) == 2

    db.session.refresh(enc)
    db.session.refresh(individual)

    # lets test the methods first
    # there is only on asset in the whole individual/encounter/sighting/asset chain so it should pass this

    assert individual.get_featured_asset_guid() == new_asset_1.guid

    sighting.add_asset(new_asset_2)
    individual.set_featured_asset_guid(new_asset_2.guid)

    assert individual.get_featured_asset_guid() == new_asset_2.guid

    # ok now the API

    patch_op = [
        utils.patch_replace_op('featuredAssetGuid', '%s' % new_asset_1.guid),
    ]

    individual_utils.patch_individual(
        flask_app_client, researcher_1, '%s' % individual.guid, patch_op
    )

    assert individual.get_featured_asset_guid() == new_asset_1.guid

    # assert new_asset_2.guid == sighting.get_featured_asset_guid()

    from app.modules.asset_groups.tasks import delete_remote

    sighting_utils.delete_sighting(flask_app_client, researcher_1, str(sighting.guid))
    delete_remote(str(new_asset_group.guid))
    asset_group_utils.delete_asset_group(
        flask_app_client, researcher_1, new_asset_group.guid
    )
