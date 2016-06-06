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

from ConfigParser import ConfigParser
from getpass import getpass
import sys
from katlibs import modules
from katlibs.main.katello_helpers import KatelloConnection
import argparse

try:
    if sys.argv[1] == '--list':
        print '\n'.join(modules.keys())
        sys.exit()
except IndexError:
    pass

parser = argparse.ArgumentParser(prog='ballista.py')
subparsers = parser.add_subparsers(help='sub-command help')
parser.add_argument('--list', help='List available actions.', action='store_true')
parser.add_argument('-c', '--conf_file', help='path to the file with the Satellite 6 config',
                    default='/etc/ballista/config.ini')
parser.add_argument('--url', help='Url to connect to (for example https://satellite6.example.com).')
parser.add_argument('-u', '--username')
parser.add_argument('-p', help='Ask for password on the command line.', action='store_true',
                    default=False, dest='password')
parser.add_argument('--organization', help='Name of the organization')

for m in modules:
    modules[m].add_to_subparsers(subparsers)

args = parser.parse_args()

config = ConfigParser()
config.read(args.conf_file)

if not args.url:
    url = config.get('main', 'url')
else:
    url = args.url

if not args.username:
    username = config.get('main', 'username')
else:
    username = args.username

if not args.organization:
    organization = config.get('main', 'organization')
else:
    organization = args.organization

if args.password:
    password = getpass('Password: ')
else:
    password = config.get('main', 'password')

passed_args = vars(args)
passed_args['connection'] = KatelloConnection(url, username, password, verify=False, organization=organization)
passed_args['config_obj'] = config

try:
    mod = modules[args.funcname].main(**passed_args)
except Exception as error:
    print error

