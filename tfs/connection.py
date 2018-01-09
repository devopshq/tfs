# -*- coding: utf-8 -*-


from urllib.parse import quote

import requests
from requests.auth import HTTPBasicAuth

from tfs.resources import *


def batch(iterable, n=1):
    """
    "batch" function that would take as input an iterable and return an iterable of iterables
    https://stackoverflow.com/a/8290508/6753144
    """
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]


class TFSAPI:
    def __init__(self, server_url, project="DefaultCollection", user=None, password=None, verify=False,
                 auth_type=HTTPBasicAuth,
                 connect_timeout=20, read_timeout=180, ):
        """
        This class must be used to get first object from TFS
        :param server_url: url to TFS server, e.g. https://tfs.example.com/
        :param project: Collection or Collection\\Project
        :param user: username, or DOMAIN\\username
        :param password: password
        :param verify: True|False - verify HTTPS cert
        :param connect_timeout: Requests CONNECTION timeout, sec or None
        :param read_timeout: Requests READ timeout, sec or None
        """
        if user is None or password is None:
            raise ValueError('User name and api-key must be specified!')
        self.rest_client = TFSHTTPClient(server_url,
                                         project=project,
                                         user=user, password=password,
                                         verify=verify,
                                         timeout=(connect_timeout, read_timeout),
                                         auth_type=auth_type,
                                         )

    def get_tfs_object(self, uri, payload=None, object_class=TFSObject, project=False):
        """ Send requests and return any object in TFS """
        raw = self.rest_client.send_get(uri=uri, payload=payload, project=project)

        # For list results
        if 'value' in raw:
            raw = raw['value']
            objects = [object_class(x, self, uri) for x in raw]
        else:
            objects = object_class(raw, self, uri)

        return objects

    def __get_workitems(self, work_items_ids, fields=None, expand='all'):
        ids_string = ','.join(map(str, work_items_ids))
        expand = '&$expand={}'.format(expand) if expand else ''
        fields_string = ('&fields=' + ','.join(fields)) if fields else ""
        workitems = self.get_tfs_object(
            'wit/workitems?ids={ids}{fields}{expand}&api-version=1.0'.format(ids=ids_string,
                                                                             fields=fields_string,
                                                                             expand=expand),
            object_class=Workitem)
        return workitems

    def get_workitem(self, id_, fields=None):
        if isinstance(id_, int):
            return self.get_workitems(id_, fields)[0]

    def get_workitems(self, work_items_ids, fields=None, batch_size=50, expand='all'):
        if isinstance(work_items_ids, int):
            work_items_ids = [work_items_ids]
        if isinstance(work_items_ids, str):
            work_items_ids = [work_items_ids]

        workitems = []
        for work_items_batch in batch(list(work_items_ids), batch_size):
            work_items_batch_info = self.__get_workitems(work_items_batch, fields=fields, expand=expand)
            workitems += work_items_batch_info
        return workitems

    def get_changesets(self, from_=None, to_=None, item_path=None, top=10000):
        payload = {'$top': top}

        if from_ and to_:
            payload['searchCriteria.fromId'] = from_
            payload['searchCriteria.toId'] = to_

        if item_path:
            payload['searchCriteria.itemPath'] = item_path
        changesets = self.get_tfs_object('tfvc/changesets', payload=payload, object_class=Changeset)
        return changesets

    def get_projects(self):
        return self.get_tfs_object('projects', object_class=Projects)

    def get_project(self, name):
        return self.get_tfs_object('projects/{}'.format(name), object_class=Projects)

    def update_workitem(self, work_item_id, update_data):
        raw = self.rest_client.send_patch('wit/workitems/{id}?api-version=1.0'.format(id=work_item_id),
                                          data=update_data,
                                          headers={'Content-Type': 'application/json-patch+json'})
        return raw

    def run_query(self, path):
        if path and not path.startswith('/'):
            path = '/' + quote(path)
        query = self.get_tfs_object('wit/queries{path}?api-version=2.2'.format(path=path),
                                    project=True,
                                    object_class=TFSQuery)
        return query

    def run_wiql(self, query):
        data = {"query": query, }
        wiql = self.rest_client.send_post('wit/wiql?api-version=1.0',
                                          data=data,
                                          project=True,
                                          headers={'Content-Type': 'application/json'}
                                          )
        return Wiql(wiql, self)

    def download_file(self, uri, filename):
        # TODO: Use download in stream, not in memory
        r = self.rest_client.send_get(uri, json=False)
        with open(filename, 'wb') as file:
            file.write(r.content)


class TFSClientError(Exception):
    pass


class TFSHTTPClient:
    def __init__(self, base_url, project, user, password, verify=False, timeout=None, auth_type=None):
        if not base_url.endswith('/'):
            base_url += '/'

        collection, project = self.get_collection_and_project(project)
        # Remove part after / in project-name, like DefaultCollection/MyProject => DefaultCollection
        # API responce only in Project, without subproject
        self._url = base_url + '%s/_apis/' % collection
        if project:
            self._url_prj = base_url + '%s/%s/_apis/' % (collection, project)
        else:
            self._url_prj = self._url

        self.http_session = requests.Session()
        auth = auth_type(user, password)
        self.http_session.auth = auth

        self.timeout = timeout
        self._verify = verify
        if not self._verify:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    @staticmethod
    def get_collection_and_project(project):
        splitted_project = project.split('/')
        collection = splitted_project[0]
        project = None

        if len(splitted_project) > 1:
            project = splitted_project[1]
            # If not space
            if project:
                project = project.split('/')[0]

        return collection, project

    def send_get(self, uri, payload=None, project=False, json=True):
        return self.__send_request('GET', uri, None, payload=payload, project=project, json=json)

    def send_post(self, uri, data, headers, project=False):
        return self.__send_request('POST', uri, data, headers, project=project)

    def send_patch(self, uri, data, headers, project=False):
        return self.__send_request('PATCH', uri, data, headers, project=project)

    def __send_request(self, method, uri, data, headers=None, payload=None, project=False, json=True):
        """
        Send request
        :param method:
        :param uri:
        :param data:
        :param headers:
        :param payload:
        :param project:
            False - add only collection to uri
            True - add Collection/Project to url, some api need it
            e.g. WIQL: https://www.visualstudio.com/en-us/docs/integrate/api/wit/wiql
        :param json:
            True - try to convert response to python-object
            False - get as is
        :return:
        """
        url = self.__prepare_uri(uri=uri, project=project)

        if method == 'POST':
            response = self.http_session.post(url, json=data, verify=self._verify, headers=headers,
                                              timeout=self.timeout)
        elif method == 'PATCH':
            response = self.http_session.patch(url, json=data, verify=self._verify, headers=headers,
                                               timeout=self.timeout)
        else:
            headers = {'Content-Type': 'application/json'}
            response = self.http_session.get(url, headers=headers, verify=self._verify, params=payload,
                                             timeout=self.timeout)
            response.raise_for_status()

        if json:
            try:
                result = response.json()

                if response.status_code != 200:
                    raise TFSClientError('TFS API returned HTTP %s (%s)' % (
                        response.status_code, result['error'] if 'error' in result else response.reason))
                return result
            except:
                raise TFSClientError('Response is not json: {}'.format(response.text))
        else:
            return response

    def __prepare_uri(self, project, uri):
        """
        Convert URI to URL
        :param project:
        :param uri:
        :return:
        """
        # TODO: Add get from non-standart collection,
        # e.g. workItemTypes: https://www.visualstudio.com/en-us/docs/integrate/api/wit/work-item-types
        if uri.startswith('https') or uri.startswith('http'):
            # If we use URL (full path)
            url = uri
        else:
            # Add prefix to uri
            url = (self._url_prj if project else self._url) + uri
        return url
