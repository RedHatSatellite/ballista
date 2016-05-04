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
            uri = 'organizations/%s/%s' % (self.orgid, uri)

        try:
            return self.session.get(
                '%s/katello/api/v2/%s?per_page=99999' % (self.base_url, uri),
                verify=self.verify,
            ).json()['results']
        except KeyError as e:
            e.message = 'Could not query Satellite 6. Maybe wrong organization or URL specified?'
            raise

    def _get_foreman_dict(self, uri):
        return self.session.get(
            '%s/api/v2/%s?per_page=99999' % (self.base_url, uri),
            verify=self.verify,
        ).json()['results']

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
