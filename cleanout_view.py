#!/usr/bin/python

from katlibs.katello_helpers import KatelloConnection
from katlibs.cview_helpers import get_components
from ConfigParser import ConfigParser
from getpass import getpass
import logging
import argparse


def main(view_name, connection):
    all_views = connection.content_views
    view_dict = get_components(all_views, ('name', view_name))
    ids_to_remove = [version['id'] for version in view_dict['versions'] if not version['environment_ids']]
    for version_id in ids_to_remove:
        logging.info('Removing version_id {}'.format(version_id))
        connection.remove_view_version(version_id)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Location of the config file', dest='conf_file')
    parser.add_argument('view_name', help='Name of the view to clean the versions of')
    args = parser.parse_args()
    config = ConfigParser()
    config.read(args.conf_file)
    url = config.get('main', 'url')
    username = raw_input('Username: ')
    password = getpass('Password: ')
    organization = config.get('main', 'organization')
    connection = KatelloConnection(url, username, password, verify=False, organization=organization)
    main(args.view_name, connection)
