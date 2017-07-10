import requests

from tfs.tfs import Workitem, Changeset, TFSObject


def batch(iterable, n=1):
    """
    Из списка возращает елементы по N штук (в другом списке)
    http://stackoverflow.com/questions/8290397/how-to-split-an-iterable-in-constant-size-chunks
    """
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


class TFSAPI:
    def __init__(self, server_url, project, user, password):
        if user is None or password is None:
            raise ValueError('User name and api-key must be specified!')
        self.rest_client = TFSClient(server_url, project=project, user=user, password=password)

    def _get_workitems(self, work_items_ids, fields=None):
        ids_string = ','.join(map(str, work_items_ids))
        fields_string = ('&fields=' + ','.join(fields)) if fields else "&$expand=all"
        workitems_raw = self.rest_client.send_get(
            'wit/workitems?ids={ids}{fields}&api-version=1.0'.format(ids=ids_string, fields=fields_string))
        workitems = [Workitem(x, self) for x in workitems_raw['value']]
        return workitems

    def get_workitems(self, work_items_ids, fields=None, batch_size=50):
        if isinstance(work_items_ids, int):
            work_items_ids = [work_items_ids]

        value = []
        for work_items_batch in batch(list(work_items_ids), batch_size):
            work_items_batch_info = self._get_workitems(work_items_batch, fields=fields)
            value += work_items_batch_info
        return value

    # TODO: Устаревшая, можно удалить
    # def get_workitems_expand_all(self, work_items_ids):
    #     ids_string = ','.join(map(str, work_items_ids))
    #     return self.rest_client.send_get(
    #         'wit/workitems?ids={ids}&$expand=all&api-version=1.0'.format(ids=ids_string))

    def get_changesets(self, From, to, itemPath=None, top=10000):
        if itemPath is None:
            payload = {'searchCriteria.fromId': From, 'searchCriteria.toId': to, '$top': top, }
        else:
            payload = {'searchCriteria.fromId': From, 'searchCriteria.toId': to, '$top': top,
                       'searchCriteria.itemPath': itemPath}
        changeset_raw = self.rest_client.send_get('tfvc/changesets', payload=payload)['value']
        changesets = [Changeset(x, self) for x in changeset_raw]
        return changesets

    # TODO: Устаревшая, можно удалить
    # def get_top_changesets(self, top):
    #     return self.rest_client.send_get('tfvc/changesets', payload={
    #         '$top': top,
    #     })

    def update_workitem(self, work_item_id, update_data):
        return self.rest_client.send_patch('wit/workitems/{id}?api-version=1.0'.format(id=work_item_id),
                                           data=update_data,
                                           headers={'Content-Type': 'application/json-patch+json'})

    def get_changeset_workitems(self, changeset_id):
        """
        Return Workitem object linked to Changeset
        :param changeset_id:
        :return:
        """
        raw = self.rest_client.send_get('tfvc/changesets/{}/workItems'.format(changeset_id))['value']
        ids = [TFSObject(x, self).id for x in raw]
        workitems = self.get_workitems(ids)
        return workitems

    def get_projects(self):
        return self.get_tfs_object('projects')

    def get_team(self, project):
        return self.get_tfs_object('projects/{}/teams'.format(project))

    def get_tfs_object(self, uri):
        """ Send requests and return any object in TFS """
        raw = self.rest_client.send_get(uri)

        # For list results
        if 'value' in raw:
            raw = raw['value']
            objects = [TFSObject(x, self) for x in raw]
        else:
            objects = TFSObject(raw, self)

        return objects


class TFSClientError(Exception):
    pass


class TFSClient:
    def __init__(self, base_url, project, user, password):
        if not base_url.endswith('/'):
            base_url += '/'
        # Remove part after / in project-name, like Development/MyProject => Development
        # API responce only in Project, without subproject
        project = project.partition('/')[0]
        self.__url = base_url + '%s/_apis/' % project
        self.__auth = (user, password)

    def send_get(self, uri, payload=None):
        return self.__send_request('GET', uri, None, payload=payload)

    def send_post(self, uri, data, headers):
        return self.__send_request('POST', uri, data, headers)

    def send_patch(self, uri, data, headers):
        return self.__send_request('PATCH', uri, data, headers)

    def __send_request(self, method, uri, data, headers=None, payload=None):
        url = self.__url + uri
        if method == 'POST':
            response = requests.post(url, auth=self.__auth, json=data, verify=False, headers=headers)
        elif method == 'PATCH':
            response = requests.patch(url, auth=self.__auth, json=data, verify=False, headers=headers)
        else:
            headers = {'Content-Type': 'application/json'}
            response = requests.get(url, auth=self.__auth, headers=headers, verify=False, params=payload)

        try:
            result = response.json()

            if response.status_code != 200:
                raise TFSClientError('TFS API returned HTTP %s (%s)' % (
                    response.status_code, result['error'] if 'error' in result else response.reason))
            return result
        except:
            raise TFSClientError('Response is not json: {}'.format(response.text))
