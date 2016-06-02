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

import logging
from ConfigParser import ConfigParser, NoOptionError
from getpass import getpass
from katlibs.main.cview_helpers import recursive_update
from katlibs.main.katello_helpers import KatelloConnection
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf_file', help='path to the file with the Satellite 6 config',
                        default='chain_config.ini')
    parser.add_argument('-d', '--debug', help='Enable debugging', default=False, action='store_true')
    parser.add_argument('view_type',
                        help='''Type of the views to promote as defined in the config file.
                        If it is not found it is presumed to be the name of a content view.''')
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    config = ConfigParser()
    config.read(args.conf_file)
    url = config.get('main', 'url')
    username = raw_input('Username: ')
    password = getpass('Password: ')
    organization = config.get('main', 'organization')

    try:
        baseviews = [v.strip() for v in config.get(args.view_type, 'views').split(',')]
    except NoOptionError:
        baseviews = [args.view_type]

    logging.debug('Updating %s' % baseviews)
    logging.debug('Using the following for building the connection')
    logging.debug('url: %s' % url)
    logging.debug('username: %s' % username)
    logging.debug('password: <redacted>')
    logging.debug('organization: %s' % organization)
    connection = KatelloConnection(url, username, password, verify=False, organization=organization)
    recursive_update(connection, baseviews)
