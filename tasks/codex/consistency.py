# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
"""
This file contains initialization data for development usage only.

You can execute this code via ``invoke codex.consistency``
"""
import logging
import tqdm

from app.extensions import db
from flask import current_app

from tasks.utils import app_context_task

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app_context_task
def user_staff_permissions(context):
    from app.modules.users.models import User

    users = User.query.all()

    updates = []
    for user in tqdm.tqdm(users):

        update = False

        if not user.in_alpha:
            user.in_alpha = True
            update = True
        if not user.in_beta:
            user.in_beta = True
            update = True

        email = user.email.strip()
        whitlist = [
            'bluemellophone@gmail.com',
            'sito.org+giraffeadmin@gmail.com',
            'sito.org+gstest@gmail.com',
        ]
        is_wildme = email.endswith('@wildme.org') or email in whitlist
        if is_wildme:
            if not user.is_staff:
                user.is_staff = True
                update = True
            if not user.is_admin:
                user.is_admin = True
                update = True
            print(user)
        else:
            if user.is_staff:
                user.is_staff = False
                update = True
            if user.is_admin:
                user.is_admin = False
                update = True

        if update:
            updates.append(user)

    with db.session.begin():
        for user in updates:
            db.session.merge(user)

    print('Updated %d users' % (len(updates),))


@app_context_task
def cleanup_gitlab(context, dryrun=False, clean=False):
    import gitlab
    import datetime
    import pytz

    TEST_GROUP_NAMES = ['TEST']
    WHITELIST_TAG = 'type:pytest-required'
    PER_PAGE = 100
    MAX_PAGES = 100
    DATETIME_FMTSTR = '%Y-%m-%dT%H:%M:%S.%fZ'
    GRACE_PERIOD = 60 * 60 * 24

    if clean:
        WHITELIST_TAG = ''
        GRACE_PERIOD = 0

    remote_uri = current_app.config.get('GITLAB_REMOTE_URI', None)
    remote_personal_access_token = current_app.config.get('GITLAB_REMOTE_LOGIN_PAT', None)

    gl = gitlab.Gitlab(remote_uri, private_token=remote_personal_access_token)
    gl.auth()
    log.info('Logged in: %r' % (gl,))

    projects = []
    groups = gl.groups.list()
    for group in groups:
        if group.name in TEST_GROUP_NAMES:
            page = 1
            log.info('Fetching projects...')
            for page in tqdm.tqdm(
                range(1, MAX_PAGES + 2), desc='Fetching GitLab Project Pages'
            ):
                projects_page = group.projects.list(
                    per_page=PER_PAGE, page=page, retry_transient_errors=True
                )

                if len(projects_page) == 0:
                    log.warning('Reached maximum page: %d' % (page,))
                    break
                elif page == MAX_PAGES + 1:
                    log.warning('More pages exist that were not processed')
                    break
                projects += projects_page
    log.info('Fetched %d projects' % (len(projects),))

    now = datetime.datetime.utcnow()
    now = now.replace(tzinfo=pytz.UTC)

    skipped = 0
    deleted = 0
    if dryrun:
        log.info('DRYRUN: Deletion skipped...')
    else:
        for project in tqdm.tqdm(projects, desc='Deleting GitLab Projects'):
            timestamp = project.last_activity_at
            timestamp = datetime.datetime.strptime(timestamp, DATETIME_FMTSTR)
            timestamp = timestamp.replace(tzinfo=pytz.UTC)
            delta = now - timestamp

            if WHITELIST_TAG in project.tag_list:
                log.info(
                    'Skipping %r (%r), marked with %r'
                    % (
                        project.name,
                        project,
                        WHITELIST_TAG,
                    )
                )
                continue
            if delta.total_seconds() <= GRACE_PERIOD:
                skipped += 1
                continue
            success = current_app.git_backend.delete_remote_project(project)
            deleted += 1 if success else 0

    log.info(
        'Deleted %d / %d projects for groups %r'
        % (
            deleted,
            len(projects),
            TEST_GROUP_NAMES,
        )
    )
    log.info(
        'Skipped %d projects last modified within the grace period (%d seconds)'
        % (
            skipped,
            GRACE_PERIOD,
        )
    )


@app_context_task
def all(context, skip_on_failure=False):
    log.info('Initializing consistency checks...')

    try:
        user_staff_permissions(context)
    except AssertionError as exception:
        if not skip_on_failure:
            log.exception('Consistency checks failed.')
        else:
            log.debug(
                'The following error was ignored due to the `skip_on_failure` flag: %s',
                exception,
            )
            log.info('Running consistency checks is skipped.')
    else:
        log.info('Consistency checks successfully applied.')
