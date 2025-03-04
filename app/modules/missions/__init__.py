# -*- coding: utf-8 -*-
"""
Missions module
============
"""

from app.extensions.api import api_v1

from app.modules import is_module_enabled

if not is_module_enabled('missions'):
    raise RuntimeError('Missions is not enabled')


def init_app(app, **kwargs):
    # pylint: disable=unused-argument,unused-variable
    """
    Init Missions module.
    """
    api_v1.add_oauth_scope('missions:read', 'Provide access to Missions details')
    api_v1.add_oauth_scope('missions:write', 'Provide write access to Missions details')
    api_v1.add_oauth_scope('missions:delete', 'Provide authority to delete Missions')

    # Touch underlying modules
    from . import models, resources  # NOQA

    api_v1.add_namespace(resources.api)
