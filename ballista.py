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
from collections import defaultdict
try:
    import argparse
except ImportError:
    import katlibs.main.argparse_local as argparse


def conf_to_dict(cfg):
    result_dict = defaultdict(dict)
    for section in cfg.sections():
        for key in config.items(section):
            result_dict[section][key[0]] = key[1]

    return result_dict

parser = argparse.ArgumentParser()
parser.add_argument('module', dest='mod_name')
parser.add_argument('action', dest='action')
parser.add_argument('--list', help='List available actions.', action='store_true', default=False)
parser.add_argument('-c', '--conf_file', help='path to the file with the Satellite 6 config',
                    default='/etc/ballista/config.ini')
parser.add_argument('--url', help='Url to connect to (for example https://satellite6.example.com).')
parser.add_argument('-u', '--username')
parser.add_argument('--organization', help='Name of the organization')
args = parser.parse_args()

if args.list:
    print '\n'.join(modules.keys())
    sys.exit()

config = ConfigParser()
conf_dict = conf_to_dict(config.read(args.conf_file))

url = conf_dict['main'].get('url', args.url)
username = conf_dict['main'].get('user', args.username)
password = conf_dict['main'].get('password', getpass('Password: '))
organization = conf_dict['main'].get('organization', args.organization)

action = modules[args.module].main
