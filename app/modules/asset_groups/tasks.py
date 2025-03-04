# -*- coding: utf-8 -*-
import logging

import git
from flask import current_app
import requests.exceptions
import sqlalchemy.exc

from app.extensions.celery import celery
from app.extensions.gitlab import GitlabInitializationError

log = logging.getLogger(__name__)


@celery.task(
    autoretry_for=(GitlabInitializationError, requests.exceptions.RequestException),
    default_retry_delay=600,
    max_retries=10,
)
def ensure_remote(asset_group_guid, additional_tags=[]):
    from .models import AssetGroup

    asset_group = AssetGroup.query.get(asset_group_guid)
    if asset_group is None:
        return  # asset group doesn't exist in the database
    project = current_app.git_backend.get_project(asset_group_guid)
    if not project:
        project = current_app.git_backend.ensure_project(
            asset_group_guid,
            asset_group.get_absolute_path(),
            asset_group.major_type.name,
            asset_group.description,
            additional_tags,
        )

    repo = asset_group.ensure_repository()
    if 'origin' not in repo.remotes:
        repo.create_remote('origin', project.ssh_url_to_repo)


@celery.task(
    autoretry_for=(GitlabInitializationError, requests.exceptions.RequestException),
    default_retry_delay=600,
    max_retries=10,
)
def delete_remote(asset_group_guid, ignore_error=True):
    try:
        current_app.git_backend.delete_remote_project_by_name(asset_group_guid)
    except (GitlabInitializationError, requests.exceptions.RequestException):
        if not ignore_error:
            raise


@celery.task(
    autoretry_for=(
        GitlabInitializationError,
        requests.exceptions.RequestException,
        git.exc.GitCommandError,
    ),
    default_retry_delay=600,
    max_retries=10,
)
def git_push(asset_group_guid):
    from .models import AssetGroup

    asset_group = AssetGroup.query.get(asset_group_guid)
    if asset_group is None:
        return  # asset group doesn't exist in the database
    repo = asset_group.get_repository()
    if 'origin' not in repo.remotes:
        ensure_remote(asset_group_guid)
    log.debug('Pushing to authorized URL')
    repo.git.push('--set-upstream', repo.remotes.origin, repo.head.ref)
    log.debug(f'...pushed to {repo.head.ref}')


@celery.task(
    autoretry_for=(requests.exceptions.RequestException, sqlalchemy.exc.SQLAlchemyError),
    default_retry_delay=10,
    max_retries=10,
)
def sage_detection(asset_group_sighting_guid, model):
    from .models import AssetGroupSighting

    asset_group_sighting = AssetGroupSighting.query.get(asset_group_sighting_guid)
    if asset_group_sighting:
        log.debug(f'Celery running sage detection for {asset_group_sighting_guid}')
        asset_group_sighting.send_detection_to_sage(model)
