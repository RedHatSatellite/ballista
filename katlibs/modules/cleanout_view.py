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

import logging
from ConfigParser import NoSectionError
from katlibs.main.katello_helpers import get_components, KatelloConnection, NotFoundError


def add_to_subparsers(subparsers):
    parser_cleanout_view = subparsers.add_parser('cleanout-view', help='Cleanup of content view versions')
    parser_cleanout_view.add_argument('content_view', nargs='*')
    parser_cleanout_view.add_argument('-a', '--all', action='store_true', default=False,
                                      help='Clean all content views', dest='all_views')
    parser_cleanout_view.add_argument('-k', '--keep', help='Keep this many of the newest unused versions',
                                      default=0, type=int)
    parser_cleanout_view.set_defaults(funcname='cleanout_view')


# noinspection PyUnusedLocal
def main(content_view, connection, all_views=False, keep=0, **kwargs):
    """
    :type keep: int or bool
    :type all_views: bool
    :type connection: KatelloConnection
    :type content_view: list
    """

    if not keep:
        keep = None

    if all_views:
        view_names = [view['name'] for view in connection.content_views]
    else:
        try:
            view_names = [c.strip() for c in kwargs['config_obj'].get(content_view[0], 'views').split(',')]
        except NoSectionError:
            view_names = content_view

    for view_name in view_names:
        try:
            view_dict = get_components(connection.content_views, ('name', view_name))
        except TypeError:
            logging.error('View %s not found!' % view_name)
            raise NotFoundError('View {} not found'.format(view_name))

        ids_to_remove = [version['id'] for version in view_dict['versions'] if not version['environment_ids']]

        try:
            ids_to_remove = sorted(ids_to_remove)[:-keep]
        except TypeError:
            pass

        for version_id in ids_to_remove:
            logging.info('Removing version_id %s' % version_id)
            connection.remove_view_version(version_id)
