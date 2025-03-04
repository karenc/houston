# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

from tests.modules.projects.resources import utils as proj_utils
import pytest

from tests.utils import module_unavailable


@pytest.mark.skipif(module_unavailable('projects'), reason='Projects module disabled')
def test_create_and_delete_project(flask_app_client, researcher_1):
    # pylint: disable=invalid-name
    from app.modules.projects.models import Project

    response = proj_utils.create_project(
        flask_app_client, researcher_1, 'This is a test project, please ignore'
    )

    project_guid = response.json['guid']
    read_project = Project.query.get(response.json['guid'])
    assert read_project.title == 'This is a test project, please ignore'
    assert read_project.owner == researcher_1

    # Try reading it back
    proj_utils.read_project(flask_app_client, researcher_1, project_guid)

    # And deleting it
    proj_utils.delete_project(flask_app_client, researcher_1, project_guid)

    read_project = Project.query.get(project_guid)
    assert read_project is None


@pytest.mark.skipif(module_unavailable('projects'), reason='Projects module disabled')
def test_project_permission(
    flask_app_client, admin_user, staff_user, researcher_1, researcher_2
):
    # Before we create any Projects, find out how many are there already
    previous_list = proj_utils.read_all_projects(flask_app_client, staff_user)

    response = proj_utils.create_project(
        flask_app_client, researcher_1, 'This is a test project, please ignore'
    )

    project_guid = response.json['guid']

    # staff user should be able to read anything
    proj_utils.read_project(flask_app_client, staff_user, project_guid)
    proj_utils.read_all_projects(flask_app_client, staff_user)

    # admin user should not be able to read any projects
    proj_utils.read_project(flask_app_client, admin_user, project_guid, 403)
    proj_utils.read_all_projects(flask_app_client, admin_user, 403)

    # user that created project can read it back plus the list
    proj_utils.read_project(flask_app_client, researcher_1, project_guid)
    list_response = proj_utils.read_all_projects(flask_app_client, researcher_1)

    # due to the way the tests are run, there may be projects left lying about,
    # don't rely on there only being one
    assert len(list_response.json) == len(previous_list.json) + 1
    project_present = False
    for project in list_response.json:
        if project['guid'] == project_guid:
            project_present = True
            break
    assert project_present

    # but a different researcher can read the list but not the project
    proj_utils.read_project(flask_app_client, researcher_2, project_guid, 403)
    proj_utils.read_all_projects(flask_app_client, researcher_2)

    # delete it
    proj_utils.delete_project(flask_app_client, researcher_1, project_guid)
