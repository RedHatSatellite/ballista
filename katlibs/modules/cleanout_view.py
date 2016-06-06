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
from katlibs.main.katello_helpers import get_components, KatelloConnection


def add_to_subparsers(subparsers):
    parser_cleanout_view = subparsers.add_parser('cleanout_view', help='Cleanup of content view versions')
    parser_cleanout_view.add_argument('view_name', nargs='?')
    parser_cleanout_view.add_argument('-k', '--keep', help='Keep this many of the newest unused versions', default=0)
    parser_cleanout_view.set_defaults(funcname='cleanout_view')


# noinspection PyUnusedLocal
def main(view_name, connection, **kwargs):
    """
    :type connection: KatelloConnection
    :type view_name: str
    """
    view_dict = get_components(connection.content_views, ('name', view_name))
    try:
        ids_to_remove = [version['id'] for version in view_dict['versions'] if not version['environment_ids']]
    except TypeError:
        logging.error('View %s not found!' % view_name)
        raise
        # TODO: generate proper raise

    for version_id in ids_to_remove:
        logging.info('Removing version_id %s' % version_id)
        connection.remove_view_version(version_id)
