# Copyright (c) 2016 the Ballista Project https://gitlab.com/parapet/ballista
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import ConfigParser
import logging
from katlibs.main.katello_helpers import get_components, KatelloConnection, get_latest_version, NoVersionError


def add_to_subparsers(subparsers):
    parser_promote_env = subparsers.add_parser('promote-env',
                                               help='Mass promote a environment to all given contentviews')
    parser_promote_env.add_argument('environment', nargs='?', help='Environment to promote to.')
    parser_promote_env.add_argument('contentviews', nargs='+',
                                    help='Specify either a ini file section or direct names of the contentview(s)')
    parser_promote_env.set_defaults(funcname='promote-env')


def mass_promote_env(connection, cvs, environment):
    """
    :param connection: The katello connection instance
    :type connection: KatelloConnection
    :param cvs: list of content view names to update
    :type cvs: list
    :type environment: str
    """
    all_views = connection.content_views
    views_to_promote = dict()

    # Get the ids of the views
    for view in all_views:
        if view['name'] in cvs:
            views_to_promote[view['name']] = view['id']

    for cvname, cvid in views_to_promote.iteritems():
        versions = get_components(connection.content_views, ('id', cvid))['versions']
        latest_version = get_latest_version(versions)

        try:
            version_id = latest_version['id']
        except KeyError:
            raise NoVersionError("no published versions found!")

        envid = get_components(connection.environments, ('name', environment))['id']
        if envid not in latest_version['environment_ids']:
            logging.info('promoting {cvname} to environment {environment}'.format(
                cvname=cvname,
                environment=environment
            ))
            connection.promote_view(version_id, {'id': version_id, 'environment_id': envid, 'force': True})


# noinspection PyUnusedLocal
def main(contentviews, connection, config_obj, environment, **kwargs):
    """
    :param contentviews: List of content views to update
    :type contentviews: list
    :param connection: The katello connection instance
    :type connection: KatelloConnection
    :param config_obj: The ini entries
    :type config_obj: ConfigParser.ConfigParser
    :type environment: str
    """
    if len(contentviews) == 1:
        config = config_obj
        try:
            cvs = [c.strip() for c in config.get(contentviews[0], 'views').split(',')]
        except ConfigParser.NoSectionError:
            cvs = contentviews
    else:
        cvs = contentviews

    mass_promote_env(connection, cvs, environment)
