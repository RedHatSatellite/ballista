#!/usr/bin/python

from katlibs.katello_helpers import KatelloConnection
from katlibs.cview_helpers import recursive_update
from ConfigParser import ConfigParser
from getpass import getpass
try:
    import argparse
except ImportError:
    import argparse_local as argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf_file', help='path to the file with the Satellite 6 config. Defaults to ./chain_config', default='chain_config.ini')
    parser.add_argument('view_type', help='Type of the views to promote as defined in the config file')
    args = parser.parse_args()
    config = ConfigParser()
    config.read(args.conf_file)
    url = config.get('main', 'url')
    username = raw_input('Username: ')
    password = getpass('Password: ')
    organization = config.get('main', 'organization')
    baseviews = [v.strip() for v in config.get(args.view_type, 'views').split(',')]
    connection = KatelloConnection(url, username, password, verify=False, organization=organization)
    recursive_update(connection, baseviews)
