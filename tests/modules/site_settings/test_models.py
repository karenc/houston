# -*- coding: utf-8 -*-
from pathlib import Path

from app.modules.fileuploads.models import FileUpload
from app.modules.site_settings.models import SiteSetting
import uuid
import pytest

from tests.utils import extension_unavailable, is_extension_enabled


def test_create_header_image(db, flask_app, test_root):
    fup = FileUpload.create_fileupload_from_path(str(test_root / 'zebra.jpg'), copy=True)
    fup2 = FileUpload.create_fileupload_from_path(str(test_root / 'fluke.jpg'), copy=True)
    with db.session.begin():
        db.session.add(fup)
        db.session.add(fup2)
    prev_site_settings = SiteSetting.query.count()
    header_image = SiteSetting.set(key='header_image', file_upload_guid=fup.guid)
    try:
        assert (
            repr(header_image)
            == f"<SiteSetting(key='header_image' file_upload_guid='{fup.guid}' public=True)>"
        )
        # Set header image again
        SiteSetting.set(key='header_image', file_upload_guid=fup2.guid)
        assert SiteSetting.query.count() == prev_site_settings + 1
    finally:
        db.session.delete(header_image)
        fup.delete()
        # The fileupload object should be deleted already
        assert FileUpload.query.filter(FileUpload.guid == fup2.guid).first() is None
        file_path = Path(fup2.get_absolute_path())
        if file_path.exists():
            file_path.unlink()


def test_create_string(db):
    new_setting = SiteSetting.set(key='site_title', string='Name of the Site')
    try:
        read_value = SiteSetting.query.get('site_title')
        assert read_value.string == 'Name of the Site'

    finally:
        db.session.delete(new_setting)


def test_get_value(db):
    # this should grab from edm and return a string
    val = SiteSetting.get_value('site.name')
    if is_extension_enabled('edm'):
        assert isinstance(val, str)
    else:
        assert val is None

    # test the default when no value
    rnd = 'test_' + str(uuid.uuid4())
    val = SiteSetting.get_value(rnd, default=rnd)
    assert val == rnd

    guid = SiteSetting.get_system_guid()
    uuid.UUID(guid, version=4)  # will throw ValueError if not a uuid
    assert guid == SiteSetting.get_value('system_guid')
    # just for kicks lets test this too
    assert guid == SiteSetting.get_string('system_guid')
    guid_setting = SiteSetting.query.get('system_guid')
    assert guid_setting is not None
    db.session.delete(guid_setting)


@pytest.mark.skipif(extension_unavailable('edm'), reason='EDM extension disabled')
def test_read_edm_configuration():
    val = SiteSetting.get_edm_configuration('site.name')
    assert isinstance(val, str)
    val = SiteSetting.get_edm_configuration('site.species')
    assert isinstance(val, list)
    try:
        val = SiteSetting.get_edm_configuration('_fu_bar_')
    except ValueError:
        pass
