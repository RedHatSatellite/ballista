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

parser_cview = subparsers.add_parser('cleanout_view', help='Cleanup of content view versions')
parser_cview.add_argument('view_name', nargs='?')
parser_cview.add_argument('-k', '--keep', help='Keep this many of the newest unused versions', default=0)
parser_cview.set_defaults(funcname='cleanout_view')

parser_promote = subparsers.add_parser('promote_chain',
                                       help='Promote a content view and all composites that contain it')
parser_promote.add_argument('view_name', nargs='?')  # TODO: we want this to be a list
parser_promote.set_defaults(funcname='promote_chain')
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
passed_args['connection'] = 'bla'  # TODO: build connection
mod = modules[args.funcname].main(**passed_args)
