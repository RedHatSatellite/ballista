#!/usr/bin/env python

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

from katlibs.katello_helpers import KatelloConnection
from katlibs.cview_helpers import get_components
from ConfigParser import ConfigParser
from getpass import getpass
import sys
import logging
try:
    import argparse
except ImportError:
    import katlibs.argparse_local as argparse


def main(view_name, connection):
    view_dict = get_components(connection.content_views, ('name', view_name))
    try:
        ids_to_remove = [version['id'] for version in view_dict['versions'] if not version['environment_ids']]
    except TypeError:
        logging.error('View {} not found!'.format(view_name))
        raise
        # TODO: generate proper raise

    for version_id in ids_to_remove:
        logging.info('Removing version_id {}'.format(version_id))
        connection.remove_view_version(version_id)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Location of the config file', dest='conf_file')
    parser.add_argument('-a', '--all', help='Clean all unused versions in all content views',
                        default=False, action='store_true')
    parser.add_argument('view_name', help='''Clean all unused versions in a specific content view'
                                          '(only required if no --all option is given)''', nargs='*')
    args = parser.parse_args()
    if not args.view_name and not args.all:
        logging.error('No view or --all argument given!')
        sys.exit(1)
    config = ConfigParser()
    config.read(args.conf_file)
    url = config.get('main', 'url')
    username = raw_input('Username: ')
    password = getpass('Password: ')
    organization = config.get('main', 'organization')
    katello_connection = KatelloConnection(url, username, password, verify=False, organization=organization)
    if args.all:
        for view in katello_connection.content_views:
            main(view['name'], katello_connection)
    else:
        main(args.view_name[0], katello_connection)
