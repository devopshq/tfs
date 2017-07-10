import requests

from tfs.tfs import *


def batch(iterable, n=1):
    """
    Из списка возращает елементы по N штук (в другом списке)
    http://stackoverflow.com/questions/8290397/how-to-split-an-iterable-in-constant-size-chunks
    """
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


class TFSAPI:
    def __init__(self, server_url, project, user, password, verify=False):
        if user is None or password is None:
            raise ValueError('User name and api-key must be specified!')
        self.rest_client = TFSClient(server_url, project=project, user=user, password=password, verify=verify)

    def get_tfs_object(self, uri, payload=None, object_class=TFSObject):
        """ Send requests and return any object in TFS """
        raw = self.rest_client.send_get(uri=uri, payload=payload)

        # For list results
        if 'value' in raw:
            raw = raw['value']
            objects = [object_class(x, self) for x in raw]
        else:
            objects = object_class(raw, self)

        return objects

    def __get_workitems(self, work_items_ids, fields=None):
        ids_string = ','.join(map(str, work_items_ids))
        fields_string = ('&fields=' + ','.join(fields)) if fields else "&$expand=all"
        workitems = self.get_tfs_object(
            'wit/workitems?ids={ids}{fields}&api-version=1.0'.format(ids=ids_string, fields=fields_string),
            object_class=Workitem)
        return workitems

    def get_workitem(self, id, fields=None):
        return self.get_workitems(id, fields)[0]

    def get_workitems(self, work_items_ids, fields=None, batch_size=50):
        if isinstance(work_items_ids, int):
            work_items_ids = [work_items_ids]
        if isinstance(work_items_ids, str):
            work_items_ids = [work_items_ids]

        workitems = []
        for work_items_batch in batch(list(work_items_ids), batch_size):
            work_items_batch_info = self.__get_workitems(work_items_batch, fields=fields)
            workitems += work_items_batch_info
        return workitems

    def get_changesets(self, from_=None, to_=None, item_path=None, top=10000):
        payload = {'$top': top}

        if from_ and to_:
            payload['searchCriteria.fromId'] = from_
            payload['searchCriteria.toId'] = to_

        if item_path:
            payload['searchCriteria.itemPath'] = item_path
        changeset_raw = self.get_tfs_object('tfvc/changesets', payload=payload, object_class=Changeset)
        changesets = [Changeset(x, self) for x in changeset_raw]
        return changesets

    def get_projects(self):
        return self.get_tfs_object('projects', object_class=Projects)

    def update_workitem(self, work_item_id, update_data):
        raw = self.rest_client.send_patch('wit/workitems/{id}?api-version=1.0'.format(id=work_item_id),
                                          data=update_data,
                                          headers={'Content-Type': 'application/json-patch+json'})
        return Workitem(raw, self)


class TFSClientError(Exception):
    pass


class TFSClient:
    def __init__(self, base_url, project, user, password, verify=False):
        if not base_url.endswith('/'):
            base_url += '/'
        # Remove part after / in project-name, like Development/MyProject => Development
        # API responce only in Project, without subproject
        project = project.partition('/')[0]
        self._url = base_url + '%s/_apis/' % project
        self._auth = (user, password)
        self._verify = verify

        if not self._verify:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def send_get(self, uri, payload=None):
        return self.__send_request('GET', uri, None, payload=payload)

    def send_post(self, uri, data, headers):
        return self.__send_request('POST', uri, data, headers)

    def send_patch(self, uri, data, headers):
        return self.__send_request('PATCH', uri, data, headers)

    def __send_request(self, method, uri, data, headers=None, payload=None):
        url = self._url + uri
        if method == 'POST':
            response = requests.post(url, auth=self._auth, json=data, verify=self._verify, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(url, auth=self._auth, json=data, verify=self._verify, headers=headers)
        else:
            headers = {'Content-Type': 'application/json'}
            response = requests.get(url, auth=self._auth, headers=headers, verify=self._verify, params=payload)
            response.raise_for_status()

        try:
            result = response.json()

            if response.status_code != 200:
                raise TFSClientError('TFS API returned HTTP %s (%s)' % (
                    response.status_code, result['error'] if 'error' in result else response.reason))
            return result
        except:
            raise TFSClientError('Response is not json: {}'.format(response.text))
