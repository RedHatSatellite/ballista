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
import time
from katlibs.main.katello_helpers import get_components, KatelloConnection, NotFoundError, get_latest_cv_version


def add_to_subparsers(subparsers):
    parser_publish_chain = subparsers.add_parser('chain-publish',
                                                 help='Publish a content view and all composites that contain it')
    parser_publish_chain.add_argument('contentviews', nargs='+',
                                      help='Specify either a ini file section or direct names of the contentview(s)')
    parser_publish_chain.set_defaults(funcname='chain_publish')


def update_and_publish_comp(connection, compview, version_dict):
    """
    Update and publish the content view with the newest version of
    the cv's passed in version_dict which looks like
    { <cv_id>: <version_id> }
    :param connection: The katello connection instance
    :type connection: KatelloConnection
    :param compview: Composite view dictionary to publish
    :type compview: dict
    :param version_dict: Dictionary containing the versions that need to be linked ({cv_id: version_id})
    :type version_dict: dict
    """

    version_list = list()

    for component in compview['components']:
        cv_id = component['content_view_id']
        try:
            version_list.append(version_dict[str(cv_id)])
        except KeyError:
            version_list.append(component['id'])

    connection.update_view(compview['id'], {
        'id': compview['id'],
        'component_ids': version_list,
    })

    connection.publish_view(compview['id'])


def recursive_update(connection, cvs, logger):
    """
    :param connection: The katello connection instance
    :type connection: KatelloConnection
    :param cvs: list of content view names to update
    :type cvs: list
    :param logger: Logger object
    :type logger: logging.RootLogger
    :return:
    """
    all_views = connection.content_views
    version_dict = dict()
    viewids_to_update = list()
    comps_to_update = list()

    # Get ids of views
    logger.debug('Determining viewids to update....')
    for view in all_views:
        viewids_to_update = viewids_to_update + [c['content_view_id'] for c in view['components'] if
                                                 c['content_view']['name'] in cvs]

    if not viewids_to_update:
        raise NotFoundError('No composite views containing any of "{}"'.format(', '.join(cvs)))

    viewids_to_update = list(set(viewids_to_update))
    logger.debug('We need to update the following ids: {}'.format(viewids_to_update))

    for cvid in viewids_to_update:
        logger.info('Publishing {}'.format(get_components(all_views, ('id', cvid))['name']))
        connection.publish_view(cvid, {'id': cvid})

    # Find which composites are impacted
    logger.debug('Check which composites we need to update')
    for view in all_views:
        if view['composite'] and set([i['content_view_id'] for i in view['components']]).intersection(
                viewids_to_update):
            logger.info('We need to update {}'.format(view['name']))
            comps_to_update.append(view)

    # Get the ids of the new versions
    logger.debug('Get version ids of the composite views')
    for cvid in viewids_to_update:
        versions = get_components(connection.content_views, ('id', cvid))['versions']
        latest_version = int(get_latest_cv_version(versions)['id'])
        version_dict[str(cvid)] = latest_version

    # Build a dictionary like:
    # {<viewid>: <latest version id>}
    latest_versions = dict()
    for viewid in viewids_to_update:
        versions = get_components(connection.content_views, ('id', viewid))['versions']
        latest_versions[str(viewid)] = get_latest_cv_version(versions)['id']

    # Wait until all the cvs are updated
    failed_content_views = list()
    while True:
        for viewid, version_id in latest_versions.iteritems():
            version_task_dict = connection.get_version_info(version_id)['last_event']['task']
            if version_task_dict['pending']:
                logger.info('Wating for content_view id {}'.format(viewid))
            elif not version_task_dict['result'] == 'success':
                failed_content_views.append(int(viewid))
                viewids_to_update.remove(int(viewid))
            else:
                viewids_to_update.remove(int(viewid))

        if len(viewids_to_update) == 0:
            logger.info('Baseviews finished updating')
            break

        logger.info('Waiting for baseviews to finish publishing, {} to go'.format(len(viewids_to_update)))
        time.sleep(10)

    if failed_content_views:
        failed_views = [get_components(all_views, ('id', failed_id))['name'] for failed_id in failed_content_views]
        logger.warning('Warning: some views failed to publish: {}'.format(failed_views))

    for view in comps_to_update:
        logger.info('Publishing {}'.format(view['name']))
        update_and_publish_comp(connection, view, version_dict)


# noinspection PyUnusedLocal
def main(contentviews, connection, logger, **kwargs):
    """
    :param contentviews: List of content views to update
    :type contentviews: list
    :param connection: The katello connection instance
    :type connection: KatelloConnection
    :param logger: Logger object
    :type logger: logging.RootLogger
    """

    if len(contentviews) == 1:
        config = kwargs['config_obj']
        try:
            cvs = [c.strip() for c in config.get(contentviews[0], 'views').split(',')]
        except ConfigParser.NoSectionError:
            cvs = contentviews
    else:
        cvs = contentviews

    try:
        recursive_update(connection, cvs, logger)
    except NotFoundError as error:
        print error
