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
from katlibs.main.katello_helpers import get_components, KatelloConnection, get_latest_version, NotFoundError


def add_to_subparsers(subparsers):
    parser_promote_env = subparsers.add_parser('promote-cv',
                                               help='Mass promote a environment to all given contentviews')
    parser_promote_env.add_argument('environment', nargs='?', help='Environment to promote to.')
    parser_promote_env.add_argument('contentviews', nargs='+',
                                    help='Specify either a ini file section or direct names of the contentview(s)')
    parser_promote_env.set_defaults(funcname='promote_cv')


def promote_cv(connection, cvname, environment, version=0):
    """
    :param connection: The katello connection instance
    :type connection: KatelloConnection
    :param cvname: name of the content view to promote
    :type cvname: str
    :type environment: str
    :param version: Version to promote, when not given latest is used
    :type version: int
    """
    all_views = connection.content_views
    try:
        cvid = get_components(all_views, ('name', cvname))['id']
    except KeyError:
        raise NotFoundError("Content view {} not found".format(cvname))

    versions = get_components(connection.content_views, ('id', cvid))['versions']
    latest_version = get_latest_version(versions)

    try:
        if version == 0:
            version_id = latest_version['id']
        else:
            version_id = get_components(versions, ('version', version))['id']
    except KeyError:
        raise NotFoundError("No published versions found of content view {}!".format(cvname))

    try:
        envid = get_components(connection.environments, ('name', environment))['id']
    except KeyError:
        raise NotFoundError("Environment {} not found".format(environment))

    if envid not in latest_version['environment_ids']:
        logging.info('promoting {cvname} to environment {environment}'.format(
            cvname=cvname,
            environment=environment
        ))
        connection.promote_view(version_id, {'id': version_id, 'environment_id': envid, 'force': True})


# noinspection PyUnusedLocal
def main(contentviews, connection, environment, config_obj=None, **kwargs):
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
        except (ConfigParser.NoSectionError, AttributeError):
            cvs = contentviews
    else:
        cvs = contentviews

    for cv in cvs:
        try:
            promote_cv(connection, cv, environment)
        except Exception as error:
            print error.message
