import requests
import sys
import json
import os


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

    def __getattr__(self, item):
        if item == 'orgid':
            if 'orgid' not in self.__dict__:
                self.orgid = self._get_orgid()
                return self.orgid
        try:
            return self._get_katello_dict('%s/' % item)
        except ValueError:
            return self._get_foreman_dict('%s/' % item)

    def _get_katello_dict(self, uri, clean=False):
        if not uri == 'organizations/' and not clean:
            uri = 'organizations/%s/%s' % (self.orgid, uri)

        return self.session.get('%s/katello/api/v2/%s?per_page=99999' % (self.base_url, uri), verify=self.verify).json()['results']

    def _get_foreman_dict(self, uri):
        return self.session.get('%s/api/v2/%s?per_page=99999' % (self.base_url, uri), verify=self.verify).json()['results']

    def _get_orgid(self):
        for org in self.organizations:
            if org['name'] == self.organization:
                return org['id']

    def get_collection_contents(self, collection_name):
        col_id = [h['id'] for h in self.host_collections if h['name'] == collection_name][0]
        return self._get_katello_dict('host_collections/%s/systems' % (col_id), clean=True)

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


def get_components(datalist, index):
    # Given a list of dictionaries, return the first key encountered in the first dict
    # so given datalist =
    # [{'name': 'name1', 'val1': 'val1'}, {'name': 'name2', 'val': 'val2'}]
    # we can get only the second item:
    # get_components(datalist, ('name', 'name2'))

    search_key = index[0]
    search_val = index[1]

    for structure in datalist:
        try:
            if structure[search_key] == search_val:
                return structure
        except KeyError:
            pass

    return None


def get_latest_version_id(version_list):
    highest_ver = sorted([float(v['version']) for v in version_list])[-1]
    try:
        return get_components(version_list, ('version', unicode(highest_ver)))['id']
    except KeyError:
        pass


def recursive_update(connection, comp_name, cvs):
    main_view = get_components(connection.content_views, ('name', comp_name))

    # Get ids of component views included in the composite view
    cvids_to_update = [c['content_view']['id'] for c in main_view['components'] if c['content_view']['name'] in cvs]
    compids_to_leave = [c['id'] for c in main_view['components'] if c['content_view']['name'] not in cvs]


    for cvid in cvids_to_update:
        connection.publish_view(cvid, {'id': cvid})

    version_id_list = list()
    
    for cvid in cvids_to_update:
        version_id_list.append(get_latest_version_id(get_components(connection.content_views, ('id', cvid))['versions']))

    version_id_list = version_id_list + compids_to_leave

    connection.update_view(main_view['id'], {
        'id': main_view['id'],
        'component_ids': version_id_list,
        })

    connection.publish_view(main_view['id'])
