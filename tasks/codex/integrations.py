# -*- coding: utf-8 -*-
import logging
import sys

from tasks.utils import app_context_task


log = logging.getLogger(__name__)


def bool_to_emoji(b):
    return '⭐' if b else '❌'


def check_db_connection(_app):
    """Check the database connection"""
    from app.extensions import db

    with db.engine.connect() as conn:
        results = conn.execute('select 1;')
        return list(results) == [(1,)]


def check_edm(app):
    """Check for connectivity to EDM"""
    try:
        app.edm._ensure_initialized()
    except Exception:
        log.exception('')
        return False
    return True


def check_edm_db(app):
    """Check for connectivity to directly to the EDM database.
    This connection is used by the indexing procedures.

    """
    from app.modules.elasticsearch.tasks import create_wildbook_engine

    engine = create_wildbook_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute('SELECT 1')
            assert result.scalar() == 1
    except Exception:
        log.exception('')
        return False
    return True


def check_gitlab(app):
    """Check the gitlab connection indirectly through the GitlabManager"""
    try:
        app.git_backend._ensure_initialized()
        app.git_backend.gl.projects.list()
    except Exception:
        log.exception('')
        return False
    return True


def check_elasticsearch(app):
    """Check the elasticsearch connection through the Elasticsearch client"""
    try:
        app.elasticsearch.info()
    except Exception:
        log.exception('')
        return False
    return True


@app_context_task()
def check(context):
    """Check integration connectivity"""
    from flask import current_app as app

    service_checks = {
        f"db ({app.config['SQLALCHEMY_DATABASE_URI']})": check_db_connection,
        'gitlab': check_gitlab,
        'edm': check_edm,
        'edm database': check_edm_db,
        'elasticsearch': check_elasticsearch,
        # ...
    }

    overall_status = True
    # Check connectivity to integration services
    for name, state_check in service_checks.items():
        status = state_check(app)
        print(f'{bool_to_emoji(status)} {name}')
        overall_status = overall_status and status

    if not overall_status:
        sys.exit(1)
