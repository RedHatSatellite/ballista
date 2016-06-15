#!/usr/bin/env python

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

import argparse
import sys
import logging
from ConfigParser import ConfigParser, NoSectionError, NoOptionError
from getpass import getpass
from katlibs import available_modules
from katlibs.main.katello_helpers import KatelloConnection


try:
    if sys.argv[1] == '--list':
        print '\n'.join(available_modules.keys())
        sys.exit()
except IndexError:
    pass


def get_from_config(config_obj, i, section='main'):
    try:
        return config_obj.get(section, i)
    except (NoSectionError, NoOptionError):
        return False

parser = argparse.ArgumentParser(prog='ballista.py')
subparsers = parser.add_subparsers(help='sub-command help')
parser.add_argument('--list', help='List available actions.', action='store_true', default=False)
parser.add_argument('-v', '--verbose', action='store_true', default=False)
parser.add_argument('-c', '--conf_file', help='path to the file with the Satellite 6 config',
                    default='/etc/ballista/config.ini')
parser.add_argument('--url', help='Url to connect to (for example https://satellite6.example.com).', default=None)
parser.add_argument('-u', '--username', default=None)
parser.add_argument('-p', help='Ask for password on the command line.', action='store_true',
                    default=False, dest='password')
parser.add_argument('--organization', help='Name of the organization', default=None)

for m in available_modules:
    available_modules[m].add_to_subparsers(subparsers)

args = parser.parse_args()
passed_args = {k: v for k, v in vars(args).iteritems() if v}
config = ConfigParser()
config.read(args.conf_file)

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

url = passed_args.get('url', get_from_config(config, 'url'))
username = passed_args.get('username', get_from_config(config, 'username'))
organization = passed_args.get('organization', get_from_config(config, 'organization'))

for item in [('url', url), ('username', username), ('organization', organization)]:
    if not item[1]:
        print "{} not specified on command line and not specified in config file".format(item[0])
        sys.exit(1)

if args.password:
    password = getpass('Password: ')
else:
    password = config.get('main', 'password')

try:
    passed_args['connection'] = KatelloConnection(url, username, password, verify=False, organization=organization)
except Exception as error:
    print "Could not set up connection:\n{}".format(error.message)
    sys.exit()

passed_args['config_obj'] = config

mod = available_modules[args.funcname]
logging.debug(
    'verbose: {verbose}\nurl: {url}\nusername: {user}\norganization: {org}\nmodule: {modname}'.format(
        verbose=args.verbose,
        url=url,
        user=username,
        org=organization,
        modname=mod.__name__,
    ))
try:
    mod.main(**passed_args)
except Exception as error:
    print "Execution failed. Error was:\n{}".format(error.message)
    sys.exit(1)
