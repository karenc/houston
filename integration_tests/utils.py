# -*- coding: utf-8 -*-
import base64
import time
import uuid


def upload_to_tus(session, codex_url, file_paths, transaction_id=None):
    if transaction_id is None:
        transaction_id = str(uuid.uuid4())

    for file_path in file_paths:
        filename = file_path.name
        encoded_filename = base64.b64encode(filename.encode('utf-8')).decode('utf-8')

        with file_path.open('rb') as f:
            content = f.read()
        length = len(content)

        response = session.post(
            codex_url('/api/v1/tus'),
            headers={
                'Upload-Metadata': f'filename {encoded_filename}',
                'Upload-Length': str(length),
                'Tus-Resumable': '1.0.0',
                'x-tus-transaction-id': transaction_id,
            },
        )
        assert response.status_code == 201
        tus_url = response.headers['Location']

        response = session.patch(
            tus_url,
            headers={
                'Tus-Resumable': '1.0.0',
                'Content-Type': 'application/offset+octet-stream',
                'Content-Length': str(length),
                'Upload-Offset': '0',
                'x-tus-transaction-id': transaction_id,
            },
            data=content,
        )
        assert response.status_code == 204
    return transaction_id


def create_new_user(session, codex_url, email, password='password', **kwargs):
    data = {'email': email, 'password': password}
    data.update(kwargs)
    response = session.post(codex_url('/api/v1/users/'), json=data)
    assert response.status_code == 200
    assert response.json()['email'] == email
    return response.json()['guid']


def create_asset_group(session, codex_url, data):

    response = session.post(
        codex_url('/api/v1/asset_groups/'),
        json=data,
    )
    print(response.json)
    print(response.text)
    assert response.status_code == 200

    json_resp = response.json()
    assert set(json_resp.keys()) >= set(
        {'guid', 'assets', 'asset_group_sightings', 'major_type', 'description'}
    )
    group_guid = json_resp['guid']
    asset_guids = [asset['guid'] for asset in json_resp['assets']]
    ags_guids = [ags['guid'] for ags in json_resp['asset_group_sightings']]
    assert len(ags_guids) == len(data['sightings'])

    assert json_resp['major_type'] == 'filesystem'
    assert json_resp['description'] == data['description']
    return group_guid, ags_guids, asset_guids


def wait_for(
    session_method,
    url,
    response_checker,
    status_code=200,
    timeout=10 * 60,
    *args,
    **kwargs,
):
    # Wait for something but have a quick nap before the first attempt to read, Sage mostly replies in this time
    # meaning that 15 second sleeps are avoided
    time.sleep(5)
    try:
        while timeout >= 0:
            response = session_method(url, *args, **kwargs)
            assert response.status_code == status_code
            if response_checker(response):
                return response
            time.sleep(15)
            timeout -= 15
        if not response_checker(response):
            assert False, f'Timed out:\n{response.json()}'
    except KeyboardInterrupt:
        print(f'The last response from {url}:\n{response.json()}')
        raise


def add_site_species(session, codex_url, data):
    site_species_url = codex_url('/api/v1/site-settings/main/site.species')
    response = session.get(site_species_url)
    values = response.json()['response']['value']
    for v in values:
        if all(v.get(k) == data[k] for k in data):
            break
    else:
        values.append(data)
        response = session.post(site_species_url, json={'_value': values})
        assert response.status_code == 200
        response = session.get(site_species_url)
    return response


def create_custom_field(session, codex_url, cls, name, type='string', multiple=False):
    config_url = codex_url('/api/v1/site-settings/main')
    response = session.post(
        config_url,
        json={
            f'site.custom.customFields.{cls}': {
                'definitions': [
                    {
                        'name': name,
                        'type': type,
                        'multiple': multiple,
                    },
                ],
            },
        },
    )
    assert response.status_code == 200
    cfd_list = response.json()['updatedCustomFieldDefinitionIds']
    return cfd_list[0]
