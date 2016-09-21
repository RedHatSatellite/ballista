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
from katlibs.main.katello_helpers import get_components, KatelloConnection, NotFoundError, get_latest_cv_version


def add_to_subparsers(subparsers):
    parser_promote_env = subparsers.add_parser('promote-cv',
                                               help='Mass promote a environment to all given contentviews')
    parser_promote_env.add_argument('environment', nargs='?', help='Environment to promote to.')
    parser_promote_env.add_argument('contentviews', nargs='+',
                                    help='Specify either a ini file section or direct names of the contentview(s)')
    parser_promote_env.set_defaults(funcname='promote_cv')


def promote_cv(connection, cvname, environment, logger, version=0):
    """
    :param connection: The katello connection instance
    :type connection: KatelloConnection
    :param cvname: name of the content view to promote
    :type cvname: str
    :type environment: str
    :param logger: Logger object
    :type logger: logging.RootLogger
    :param version: Version to promote, when not given latest is used
    :type version: int
    """

    logger.debug('Getting all content views')
    all_views = connection.content_views
    try:
        logger.debug('Get content view id of {}'.format(cvname))
        cvid = get_components(all_views, ('name', cvname))['id']
        logger.debug('ID is {}'.format(cvid))
    except KeyError:
        logger.error("Content view {} not found".format(cvname))
        raise NotFoundError("Content view {} not found".format(cvname))

    logger.debug('Get all version ids')
    versions = get_components(connection.content_views, ('id', cvid))['versions']
    logger.debug('Found: {}'.format(versions))
    logger.debug('Get latest version id')
    latest_version = get_latest_cv_version(versions)
    logger.debug('Latest version id: {}'.format(latest_version))

    try:
        if version == 0:
            version_id = latest_version['id']
            logger.debug(
                'We are going to promote the latest version (id: {}, name: {}) to {}'.format(
                    version_id, version, environment),
            )
        else:
            version_id = get_components(versions, ('version', version))['id']
            logger.debug('We are going to promote {} (id: {}) to {}'.format(version, version_id, environment))
    except KeyError:
        logger.error("No published versions found of content view {}!".format(cvname))
        raise NotFoundError("No published versions found of content view {}!".format(cvname))

    try:
        logger.debug('Get environment id for {}'.format(environment))
        envid = get_components(connection.environments, ('name', environment))['id']
        logger.debug('Environment id is {}'.format(envid))
    except KeyError:
        logger.error("Environment {} not found".format(environment))
        raise NotFoundError("Environment {} not found".format(environment))

    if envid not in latest_version['environment_ids']:
        logger.info('promoting {cvname} to environment {environment}'.format(
            cvname=cvname,
            environment=environment
        ))
        connection.promote_view(version_id, {'id': version_id, 'environment_id': envid, 'force': True})


# noinspection PyUnusedLocal
def main(contentviews, connection, environment, logger, config_obj=None, **kwargs):
    """
    :param contentviews: List of content views to update
    :type contentviews: list
    :param connection: The katello connection instance
    :type connection: KatelloConnection
    :param logger: Logger object
    :type logger: logging.RootLogger
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
            promote_cv(connection, cv, environment, logger)
        except Exception as error:
            print error.message
