# Copyright (c) 2016 Yoram Hekma <hekma.yoram@gmail.com>
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

import time
import logging


def get_running_publishes(tasklist):
    logging.debug('Check for running publish tasks')
    # Returns a list of content view ids that are being published
    running_publishes = list()
    for task in tasklist:
        if task['state'] == 'running' and task['label'] == 'Actions::Katello::ContentView::Publish':
            logging.debug('Publish task %s is still running' % task)
            running_publishes.append(task['input']['content_view']['id'])

    return running_publishes


def get_components(datalist, index):
    # Given a list of dictionaries, return the first key encountered in the first dict
    # so given datalist =
    # [{'name': 'name1', 'val1': 'val1'}, {'name': 'name2', 'val': 'val2'}]
    # we can get only the second item:
    # get_components(datalist, ('name', 'name2'))

    search_key = index[0]
    search_val = index[1]

    for structure in datalist:
        try:
            if structure[search_key] == search_val:
                return structure
        except KeyError:
            pass

    return None


def get_latest_version_id(version_list):
    highest_ver = sorted([float(v['version']) for v in version_list])[-1]
    try:
        return get_components(version_list, ('version', unicode(highest_ver)))['id']
    except KeyError:
        pass


def update_and_publish_comp(connection, compview, version_dict):
    # Update and publish the content view with the newest version of
    # the cv's passed in version_dict which looks like
    # { <cv_id>: <version_id> }

    version_list = list()

    logging.debug('Getting component content view ids from %s' % compview['name'])
    for component in compview['components']:
        cv_id = component['content_view_id']
        logging.debug('%s --> %s' % (component['name'], cv_id))
        try:
            logging.debug('Version updated, registering new version id')
            version_list.append(version_dict[str(cv_id)])
        except KeyError:
            logging.debug('Version unchanged')
            version_list.append(component['id'])

    logging.debug('Updating %s with new component ids %s' % (compview['name'], version_list))
    connection.update_view(compview['id'], {
        'id': compview['id'],
        'component_ids': version_list,
    })

    logging.debug('Publishing %s' % (compview['name']))
    connection.publish_view(compview['id'])


def recursive_update(connection, cvs):
    logging.debug('Going to update %s' % cvs)
    logging.debug('Get all content views')
    all_views = connection.content_views
    version_dict = dict()
    viewids_to_update = list()
    comps_to_update = list()

    # Get ids of views
    logging.debug('Getting ids of views that need to be updated')
    for view in all_views:
        viewids_to_update = viewids_to_update + [c['content_view_id'] for c in view['components'] if
                                                 c['content_view']['name'] in cvs]

    viewids_to_update = list(set(viewids_to_update))

    for cvid in viewids_to_update:
        logging.info('Publishing id %s' % cvid)
        connection.publish_view(cvid, {'id': cvid})

    # Find which composites are impacted
    logging.debug('Check which composite content views need to be updated')
    for view in all_views:
        if view['composite'] and set([i['content_view_id'] for i in view['components']]).intersection(
                viewids_to_update):
            logging.debug('%s is composite and needs to be updated' % view['name'])
            comps_to_update.append(view)

    # Get the ids of the new versions
    logging.debug('Check ids of the new versions')
    for cvid in viewids_to_update:
        logging.debug('Check cvid %s' % cvid)
        versions = get_components(connection.content_views, ('id', cvid))['versions']
        latest_version = get_latest_version_id(versions)
        logging.debug('Latest version id: %s' % latest_version)
        version_dict[str(cvid)] = latest_version

    # Wait until all the cvs are updated
    while True:
        if set(get_running_publishes(connection.foreman_tasks)).intersection(viewids_to_update):
            logging.info('Waiting for base content views to finish...')
            time.sleep(10)
        else:
            break

    for view in comps_to_update:
        logging.info('Update and publish %s' % view['name'])
        update_and_publish_comp(connection, view, version_dict)
