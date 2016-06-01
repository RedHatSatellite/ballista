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


import requests
import json


def to_dict(result_list):
    ret_dict = dict()
    for item in result_list:
        ret_dict[item['name']] = item

    return ret_dict


class KatelloConnection(object):
    def __init__(self, base_url, username, password, verify, organization):
        self.organization = organization
        self.base_url = base_url
        self.verify = verify
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.post_headers = {'Content-Type': 'application/json'}
        if not verify:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def _query_api(self, url):
        if url.endswith('/'):
            url = url[:-1]

        counter = 1
        results = list()

        while True:
            page_result = self.session.get('%s?page=%s' % (url, counter), verify=self.verify).json()['results']
            if not page_result:
                break
            results += page_result
            counter += 1

        return results

    def __getattr__(self, item):
        if item == 'orgid':
            if 'orgid' not in self.__dict__:
                self.orgid = self._get_orgid()
                return self.orgid

        if item == 'foreman_tasks':
            return self.session.get('%s/foreman_tasks/api/tasks' % self.base_url, verify=self.verify).json()['results']

        try:
            return self._get_katello_dict('%s/' % item)
        except ValueError:
            return self._get_foreman_dict('%s/' % item)

    def _get_katello_dict(self, uri, clean=False):
        if not uri == 'organizations/' and not clean:
            try:
                return self._query_api('%s/katello/api/v2/organizations/%s/%s' % (self.base_url, self.orgid, uri))
            except ValueError:
                pass

        return self._query_api('%s/katello/api/v2/%s' % (self.base_url, uri))

    def _get_foreman_dict(self, uri):
        return self._query_api('%s/api/v2/%s' % (self.base_url, uri))

    def _get_orgid(self):
        for org in self.organizations:
            if org['name'] == self.organization:
                return org['id']

    def get_collection_contents(self, collection_name):
        col_id = [h['id'] for h in self.host_collections if h['name'] == collection_name][0]
        return self._get_katello_dict('host_collections/%s/systems' % col_id, clean=True)

    def publish_view(self, c_id, data=None):
        return self.session.post(
            '%s/katello/api/content_views/%s/publish' % (self.base_url, c_id),
            data=json.dumps(data),
            headers=self.post_headers,
        ).json()

    def update_view(self, c_id, data=None):
        return self.session.put(
            '%s/katello/api/content_views/%s' % (self.base_url, c_id),
            data=json.dumps(data),
            headers=self.post_headers,
        ).json()

    def remove_view_version(self, v_id):
        return self.session.delete(
            '%s/katello/api/content_view_versions/%s' % (self.base_url, v_id),
            headers=self.post_headers,
        ).json()
