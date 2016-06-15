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


import requests
import json
import sys


class KatelloConnection(object):
    def __init__(self, base_url, username, password, verify, organization):
        """
        :param base_url: Url to connect to
        :type base_url: str
        :param username: Username for querying
        :type username: str
        :param password: Password for querying
        :type password: str
        :param verify: Whether to accept self-signed ssl
        :type verify: bool
        :param organization: Organization to use
        :type organization: str
        :returns: KatelloConnection object
        :rtype: KatelloConnection
        """
        self.organization = organization
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = verify
        self.post_headers = {'Content-Type': 'application/json'}
        if not verify:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def _query_api(self, url):
        """
        Succesively query the API, appending "?page=<int>" to the url, each time incrementing the int by one.
        When we get no results, return the collected data.

        :param url: Url that needs to be concatenated to the base_url
        :type url: str
        :return: List of dictionaries as returned from the api ['results']
        :rtype: list
        """
        if url.endswith('/'):
            url = url[:-1]

        counter = 1
        results = list()

        while True:
            page_result = self.session.get(url, params={'page': counter}).json()['results']
            if not page_result:
                break
            results += page_result
            counter += 1

        return results

    def __getattr__(self, item):
        """
        Dynamically defer the requested attribute to the API

        :param item: The attribute we want (content_views, organizations, etc)
        :type item: str
        :return: List of dictionaries as returned from the api call ['results']
        :rtype: list
        """
        if item == 'orgid':
            if 'orgid' not in self.__dict__:
                self.orgid = self._get_orgid()
                return self.orgid

        if item == 'foreman_tasks':
            return self.session.get('%s/foreman_tasks/api/tasks' % self.base_url).json()['results']

        try:
            return self._get_katello_dict('%s/' % item)
        except ValueError:
            return self._get_foreman_dict('%s/' % item)

    def _get_katello_dict(self, uri, clean=False):
        """
        Call the katello api (https://url/katello/api/v2)

        :param uri: Url to query
        :type uri: str
        :param clean: When true, we do not want to use the organization part in the url
        :type clean: bool
        :return: List of dictionaries as returned from the api call ['results']
        :rtype: list
        """
        if not uri == 'organizations/' and not clean:
            try:
                return self._query_api('%s/katello/api/v2/organizations/%s/%s' % (self.base_url, self.orgid, uri))
            except ValueError:
                pass

        return self._query_api('%s/katello/api/v2/%s' % (self.base_url, uri))

    def _get_foreman_dict(self, uri):
        """
        Call the foreman api (https://url/api/v2)

        :param uri: Url to query
        :return: List of dictionaries as returned from the api call ['results']
        :rtype: list
        """
        return self._query_api('%s/api/v2/%s' % (self.base_url, uri))

    def _get_orgid(self):
        """
        Get the organizational id of our organization

        :rtype: int
        """
        for org in self.organizations:
            if org['name'] == self.organization:
                return org['id']

    def get_collection_contents(self, collection_name):
        """
        Get the hosts that belong to a host_collection

        :param collection_name: Name of the host_collection to query
        :type collection_name: str
        :return: List of host dicts
        :rtype: list
        """
        col_id = [h['id'] for h in self.host_collections if h['name'] == collection_name][0]
        return self._get_katello_dict('host_collections/%s/systems' % col_id, clean=True)

    def publish_view(self, c_id, data=None):
        """
        :param c_id: content view id
        :type c_id: int or str
        :param data: Additional post data
        :type data: dict
        :return: json output of the api query
        :rtype: dict
        """
        return self.session.post(
            '%s/katello/api/content_views/%s/publish' % (self.base_url, c_id),
            data=json.dumps(data),
            headers=self.post_headers,
        ).json()

    def update_view(self, c_id, data=None):
        """
        :param c_id: content view id
        :type c_id: int or str
        :param data: Additional post data
        :type data: dict
        :return: json output of the api query
        """
        return self.session.put(
            '%s/katello/api/content_views/%s' % (self.base_url, c_id),
            data=json.dumps(data),
            headers=self.post_headers,
        ).json()

    def remove_view_version(self, v_id):
        """
        :param v_id: content view id
        :type v_id: int or str
        :return: json output of the api query
        """
        return self.session.delete(
            '%s/katello/api/content_view_versions/%s' % (self.base_url, v_id),
            headers=self.post_headers,
        ).json()

    def promote_view(self, v_id, data=None):
        return self.session.post(
            '%s/katello/api/content_view_versions/%s/promote' % (self.base_url, v_id),
            data=json.dumps(data),
            headers=self.post_headers,
        ).json()


def get_components(datalist, index):
    """
    Given a list of dictionaries, return the first key encountered in the first dict
    so given datalist =
    [{'name': 'name1', 'val1': 'val1'}, {'name': 'name2', 'val': 'val2'}]
    we can get only the second item:
    get_components(datalist, ('name', 'name2'))

    :param datalist: List of dictionaries to search in
    :type datalist: list
    :param index: Tuple to search for. Index0 is the key, Index1 the value
    :type index: tuple
    :return: The dictionary that matches when found, else None
    :rtype: dict
    """

    search_key = index[0]
    search_val = index[1]

    for structure in datalist:
        try:
            if structure[search_key] == search_val:
                return structure
        except KeyError:
            pass

    return dict()


def get_latest_version(version_list):
    """
    :param version_list: List of version dictionaries as returned by api (versions property of a view)
    :type version_list: list
    :returns: The id of the latest version
    :rtype: dict
    """
    try:
        highest_ver = sorted([float(v['version']) for v in version_list])[-1]
        return get_components(version_list, ('version', unicode(highest_ver)))
    except KeyError:
        pass
    except IndexError:
        return dict()


class NoComposites(Exception):
    def __init__(self, message):
        print message
        sys.exit(1)


class NotFoundError(Exception):
    def __init__(self, message):
        print message
        sys.exit(1)
