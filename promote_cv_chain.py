#!/usr/bin/python

from katlibs.katello_helpers import KatelloConnection
from katlibs.cview_helpers import recursive_update
from ConfigParser import ConfigParser
from getpass import getpass
import argparse
import logging


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf_file', help='path to the file with the Satellite 6 config', default='chain_config.ini')
    parser.add_argument('-d', '--debug', help='Enable debugging', default=False, action='store_true')
    parser.add_argument('view_type', help='Type of the views to promote as defined in the config file')
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
    baseviews = [v.strip() for v in config.get(args.view_type, 'views').split(',')]
    logging.debug('Updating {}'.format(baseviews))
    logging.debug('Using the following for building the connection')
    logging.debug('url: {}'.format(url))
    logging.debug('username: {}'.format(username))
    logging.debug('password: <redacted>')
    logging.debug('organization: {}'.format(organization))
    connection = KatelloConnection(url, username, password, verify=False, organization=organization)
    recursive_update(connection, baseviews)
