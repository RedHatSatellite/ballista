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

import ConfigParser
import time
import json
import os
from katlibs.main.katello_helpers import get_components, KatelloConnection, NotFoundError


def add_to_subparsers(subparsers):
    parser_compute_resource_profiles = subparsers.add_parser('compute-resource-profiles',
                                                 help='Export or import compute resource profiles')
    parser_compute_resource_profiles.add_argument('-cr', '--compute-resource', help='Specify the compute resource', required=True)
    iogroup = parser_compute_resource_profiles.add_mutually_exclusive_group(required=True)
    iogroup.add_argument('-e', '--export-profiles', action='store_true', default=False, help='Specify the path to export the profiles to in JSON format')
    iogroup.add_argument('-i', '--import-profiles', action='store_true', default=False, help='Specify the profile path with the JSON files to import the profiles')
    parser_compute_resource_profiles.add_argument('-p', '--path', help='Specify the profile export/import path', required=True)
    parser_compute_resource_profiles.set_defaults(funcname='compute_resource_profiles')


def export_compute_profiles(compute_resource, path, connection, logger):
    """
    :param compute_resource: The compute resource name
    :type compute_resource: str
    :param path: The file path to work with
    :type path: str
    :param connection: The katello connection instance
    :type connection: KatelloConnection
    :param logger: Logger object
    :type logger: logging.RootLogger
    :return:
    """

    logger.debug('Getting the compute resources')
    compute_resources = connection.compute_resources

    try:
        logger.debug('Get compute resource id of {}'.format(compute_resource))
        crid = get_components(compute_resources, ('name', compute_resource))['id']
        logger.debug('ID is {}'.format(crid))
    except KeyError:
        logger.error("Compute resource {} not found".format(compute_resource))
        raise NotFoundError("Compute resource {} not found".format(compute_resource))

    logger.debug('Getting the ids of the compute profiles')
    compute_profile_ids = [profile['id'] for profile in connection.compute_profiles]

    logger.debug('Getting the profiles for compute resource ()'.format(compute_resource))
    compute_profiles = [connection.get_compute_profiles(pid) for pid in compute_profile_ids]

    logger.debug('Checking if the compute profiles are related to the compute resource')
    for profile in compute_profiles:
        for compute_attribute in profile['compute_attributes']:
            if compute_attribute['compute_resource_name'] == compute_resource:
                with open(path+'/'+compute_attribute['compute_profile_name']+'.json', 'w') as outfile:
                    json.dump(compute_attribute, outfile)


def import_compute_profiles(compute_resource, path, connection, logger):
    """
    :param compute_resource: The compute resource name
    :type compute_resource: str
    :param path: The file path to work with
    :type path: str
    :param connection: The katello connection instance
    :type connection: KatelloConnection
    :param logger: Logger object
    :type logger: logging.RootLogger
    :return:
    """

    logger.debug('Getting the compute resources')
    compute_resources = connection.compute_resources

    try:
        logger.debug('Get compute resource id of {}'.format(compute_resource))
        crid = get_components(compute_resources, ('name', compute_resource))['id']
        logger.debug('ID is {}'.format(crid))
    except KeyError:
        logger.error("Compute resource {} not found".format(compute_resource))
        raise NotFoundError("Compute resource {} not found".format(compute_resource))

    logger.debug('Restoring the compute profiles')
    for profile in os.listdir(path):
        json_data = '{ "compute_profile": { "name": "%s" } }' % profile.split('.json')[0]
        cpid = connection.create_compute_profile(json_data)

        with open(path+'/'+profile) as cp_file:
            pdata = json.load(cp_file)

        compute_attribute = dict()
        compute_attribute['vm_attrs'] = pdata['vm_attrs']
        connection.add_compute_attributes(crid, cpid['id'], compute_attribute)

# noinspection PyUnusedLocal
def main(connection, logger, compute_resource, path, export_profiles=None, import_profiles=None, **kwargs):
    """
    :param connection: The katello connection instance
    :type connection: KatelloConnection
    :param logger: Logger object
    :type logger: logging.RootLogger
    :param compute_resource: The compute resource name
    :type compute_resource: str
    :param path: The file path to work with
    :type path: str
    :type export_profiles: bool
    :type import_profiles: bool
    """

    if export_profiles:
        try:
            export_compute_profiles(compute_resource, path, connection, logger)
        except NotFoundError as error:
            print error
    elif import_profiles:
        try:
            import_compute_profiles(compute_resource, path, connection, logger)
        except NotFoundError as error:
            print error