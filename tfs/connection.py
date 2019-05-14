# -*- coding: utf-8 -*-
from urllib.parse import quote

import base64
import requests
from requests.auth import HTTPBasicAuth

from tfs.resources import *  # noqa


def batch(iterable, n=1):
    """
    "batch" function that would take as input an iterable and return an iterable of iterables
    https://stackoverflow.com/a/8290508/6753144
    """
    len_ = len(iterable)
    for ndx in range(0, len_, n):
        yield iterable[ndx:min(ndx + n, len_)]


class TFSAPI:
    def __init__(self, server_url, project="DefaultCollection", user=None, password=None, pat=None, verify=False,
                 auth_type=HTTPBasicAuth,
                 connect_timeout=20, read_timeout=180):
        """
        This class must be used to get first object from TFS

        :param server_url: url to TFS server, e.g. https://tfs.example.com/
        :param project: Collection or Collection\\Project
        :param user: username, or DOMAIN\\username
        :param password: password
        :param pat: personal access token
        :param verify: True|False - verify HTTPS cert
        :param connect_timeout: Requests CONNECTION timeout, sec or None
        :param read_timeout: Requests READ timeout, sec or None
        """
        if auth_type is HTTPBasicAuth:
            if (user is None or password is None) and pat is None:
                raise ValueError('User name and password or personal access token must be specified!')
        self.rest_client = TFSHTTPClient(server_url,
                                         project=project,
                                         user=user, password=password, pat=pat,
                                         verify=verify,
                                         timeout=(connect_timeout, read_timeout),
                                         auth_type=auth_type,
                                         )

    def get_tfs_resource(self, uri, underProject=None, payload=None):
        """ Return any object in TFS by the uri """
        raw = self.get_json(uri=uri, underProject=underProject, payload=payload)

        # For list results
        if 'value' in raw:
            raw = raw['value']
            url = raw[0].get('url', '') if raw else ''
            tfs_class = class_for_resource(url)
            return [tfs_class(tfs=self, raw=x, listVersion=True) for x in raw]
        else:
            return class_for_resource(raw['url'])(tfs=self, raw=raw, listVersion=False)

    def _find_resource(self, resource_class, ids=None):
        """
        Find resource by name and ids
        """
        resource = resource_class(tfs=self)
        if ids is not None:
            resource._find(ids)
        return resource

    def get_json(self, uri, underProject=None, payload=None):
        """ Get resource from known location or try both locations
            (under collection and under collection/project)

        :param uri: uri of he resource
        :param underProject: base resource location selector
        :param payload: additional query attributes
        """
        if underProject is not None:
            return self.rest_client.send_get(uri, payload=payload, project=underProject)
        else:
            try:
                return self.rest_client.send_get(uri, payload=payload, project=True)
            except Exception:
                return self.rest_client.send_get(uri, payload=payload, project=False)

    def substitute_ids(self, uri, ids):
        """ Substitute id placeholders in the uri

        :param uri: uri with id placeholders
        :type uri: str
        :param ids: ids to replace placeholders in the uri
        :type ids: Union[Tuple[str, str], int, str]
        """
        if isinstance(ids, tuple):
            return uri.format(*ids)

        return uri.format(ids)

    def __get_workitems(self, work_items_ids, fields=None, expand='all'):
        ids_string = ','.join(map(str, work_items_ids))
        expand = '&$expand={}'.format(expand) if expand else ''
        fields_string = ('&fields=' + ','.join(fields)) if fields else ""
        workitems = self.get_tfs_resource(
            'wit/workitems?ids={ids}{fields}{expand}&api-version=1.0'.format(ids=ids_string,
                                                                             fields=fields_string,
                                                                             expand=expand),
            underProject=False)
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

    def get_changeset(self, id):
        return self._find_resource(Changeset, ids=id)

    def get_changesets(self, from_=None, to_=None, item_path=None, top=10000):
        payload = {'$top': top}

        if from_:
            from_ = str(from_)
            if from_.isdigit():
                payload['searchCriteria.fromId'] = from_
            else:
                raise ValueError('from_ must be valid TFS changeset IDs!')

        if to_:
            to_ = str(to_)
            if to_.isdigit():
                payload['searchCriteria.toId'] = to_
            else:
                raise ValueError('to_ must be valid TFS changeset IDs!')

        if item_path:
            payload['searchCriteria.itemPath'] = item_path
        changesets = self.get_tfs_resource('tfvc/changesets', underProject=False, payload=payload)
        return changesets

    def get_projects(self):
        """ Deprecated. Use projects instead """
        return self.projects

    def get_project(self, name):
        """ Deprecated. Use project instead"""
        return self.project(name)

    @property
    def projects(self):
        """ List of all projects """
        return self.get_tfs_resource('projects', underProject=False)

    def project(self, id):
        """ Get project by id """
        return self._find_resource(Project, id)

    def teams(self, projectId):
        """ List of teams under the project

        :param projectId: id of the project
        """
        return self.get_tfs_resource('projects/{}/teams'.format(projectId), underProject=False)

    def builds(self):
        return self.get_tfs_resource('build/builds', underProject=True)

    def build(self, id):
        """ Get build by id

        :param id: id of the build
        :return: Build class
        """
        return self._find_resource(Build, ids=id)

    def definitions(self, nameFilter=None):
        """ List of build definitions

        :param name: Filters to definitions whose names equal this value.
                     Use ``*`` as a wildcard, ex: 'Release_11.*' or 'Release_*_11.0'
        :return: list of :class:`Definition` object
         """
        if nameFilter:
            payload = {'name': nameFilter}
        return self.get_tfs_resource('build/definitions', underProject=True, payload=payload)

    def definition(self, id):
        return self._find_resource(Definition, ids=id)

    def runs(self, top=None):
        if top is None:
            top = 100
        payload = {'$top': top}

        return self.get_tfs_resource('test/runs', underProject=True, payload=payload)

    def run(self, id):
        return self._find_resource(Run, ids=id)

    def results(self, runId, top=None):
        if top is None:
            top = 100
        payload = {'$top': top}
        return self.get_tfs_resource('test/runs/{}/results'.format(runId), underProject=True, payload=payload)

    def result(self, runId, resultId):
        return self._find_resource(Result, ids=(runId, resultId))

    # not a resource
    def update_workitem(self, work_item_id, update_data, params=None):
        raw = self.rest_client.send_patch('wit/workitems/{id}?api-version=1.0'.format(id=work_item_id),
                                          data=update_data,
                                          headers={'Content-Type': 'application/json-patch+json'},
                                          payload=params)
        return raw

    def run_query(self, path):
        """ Get query definition by path
            and get Wiql of this query results in the self.result
        """
        if path and not path.startswith('/'):
            path = '/' + quote(path)
        return self._find_resource(TFSQuery, ids=path)

    def run_saved_query(self, id):
        """ Run saved query by query id

        :param id: id of the query to run
        :return: instance of the Wiql object with query results
        """
        return self._find_resource(Wiql, ids=id)

    def run_wiql(self, query, params=None):
        data = {"query": query, }
        if params is None:
            params = {}
        if 'api-version' not in params:
            params['api-version'] = '1.0'
        wiql = self.rest_client.send_post('wit/wiql',
                                          data=data,
                                          project=True,
                                          payload=params
                                          )
        return Wiql(self, wiql)

    def download_file(self, uri, filename):
        # TODO: Use download in stream, not in memory
        r = self.rest_client.send_get(uri, json=False)
        with open(filename, 'wb') as file:
            file.write(r.content)

    def get_gitrepositories(self):
        return self.get_tfs_resource('git/repositories', underProject=False)

    def get_gitrepository(self, name):
        return self._find_resource(GitRepository, ids=name)

    def __create_workitem(self, type_, data=None, validate_only=None, bypass_rules=None,
                          suppress_notifications=None,
                          api_version=1.0):
        """
        Create work item. Param description: https://docs.microsoft.com/en-us/rest/api/vsts/wit/work%20items/create

        :param project: Name of the target project. The same project is used by default.
        :return: Raw JSON of the work item created
        """
        uri = 'wit/workitems/${type}'.format(type=type_)
        params = {'api-version': api_version, 'validateOnly': validate_only, 'bypassRules': bypass_rules,
                  'suppressNotifications': suppress_notifications}

        headers = {'Content-Type': 'application/json-patch+json'}
        raw = self.rest_client.send_post(uri=uri, data=data, headers=headers, project=True, payload=params)
        return raw

    def create_workitem(self, type_, fields=None, relations_raw=None, validate_only=None, bypass_rules=None,
                        suppress_notifications=None,
                        api_version=1.0):
        """
        Create work item. Doc: https://docs.microsoft.com/en-us/rest/api/vsts/wit/work%20items/create

        :param type_: Work item
        :param fields: Dictionary containing field values
        :param relations_raw: List containing relations which are dict(rel, url[, attributes])
        :param validate_only: When True, do not actually create a work item, a dry run of sorts
        :param bypass_rules: When True, can bypass restrictions like <ALLOWEDVALUES> and such
        :param suppress_notifications: When true, notifications are [supposedly] not sent
        :param api_version: API version to use
        :return: WorkItem instance of a newly created WI
        """

        # fields
        body = [dict(op="add", path='/fields/{}'.format(name), value=value) for name, value in fields.items()] \
            if fields else []
        # relations
        if relations_raw:
            body.extend([dict(op="add", path='/relations/-', value=relation) for relation in relations_raw])

        raw = self.__create_workitem(type_, body, validate_only, bypass_rules, suppress_notifications,
                                     api_version)

        return Workitem(self, raw)

    def __adjusted_area_iteration(self, value):
        """
        Adapt area or iteration path from the old TeamProject to the current one. Used when copying work items from
        different projects.
        :param value: Old area/iteration path value.
        :return: Value with the project part replaced.
        """
        actual_area = value.split('\\')[1:]
        actual_area.insert(0, self.rest_client.project)
        return '\\'.join(actual_area)

    def copy_workitem(self, workitem, with_links_and_attachments=False, from_another_project=False, target_type=None,
                      target_area=None,
                      target_iteration=None,
                      validate_only=None,
                      bypass_rules=None,
                      suppress_notifications=None,
                      api_version=1.0):
        """
        Create a copy of a work item

        :param workitem: Source workitem
        :param with_links_and_attachments: When True, all relations are copied
        :param from_another_project: When True, certain fields are not copied
        :param target_type: When specified, the copy will have this type instead of the source one
        :param target_area: When specified, the copy will have this area instead of the source one
        :param target_iteration: When specified, the copy will have this iteration instead of the source one
        :param validate_only: When True, do not actually create a work item, a dry run of sorts
        :param bypass_rules: When True, can bypass restrictions like <ALLOWEDVALUES> and such
        :param suppress_notifications: When true, notifications are [supposedly] not sent
        :param api_version: API version to use
        :return: WorkItem instance of a newly created copy
        """

        fields = workitem.data.get('fields')
        type_ = target_type if target_type else fields['System.WorkItemType']

        params = {'api-version': api_version, 'validateOnly': validate_only, 'bypassRules': bypass_rules,
                  'suppressNotifications': suppress_notifications}

        # When copy from another project, adjust AreaPath and IterationPath and do not copy identifying fields
        if from_another_project:
            no_copy_fields = ['System.TeamProject',
                              'System.AreaPath',
                              'System.IterationPath',
                              'System.Id',
                              'System.AreaId',
                              'System.NodeName',
                              'System.AreaLevel1',
                              'System.AreaLevel2',
                              'System.AreaLevel3',
                              'System.AreaLevel4',
                              'System.Rev',
                              'System.AutorizedDate',
                              'System.RevisedDate',
                              'System.IterationId',
                              'System.IterationLevel1',
                              'System.IterationLevel2',
                              'System.IterationLevel4',
                              'System.CreatedDate',
                              'System.CreatedBy',
                              'System.ChangedDate',
                              'System.ChangedBy',
                              'System.AuthorizedAs',
                              'System.AuthorizedDate',
                              'System.Watermark']

            fields = {}
            for name, value in workitem.fields.items():
                if name in no_copy_fields:
                    continue
                fields[name] = value

            fields['System.AreaPath'] = target_area \
                if target_area else self.__adjusted_area_iteration(workitem['AreaPath'])
            fields['System.IterationPath'] = target_iteration \
                if target_iteration else self.__adjusted_area_iteration(workitem['IterationPath'])

        relations = None

        wi = self.create_workitem(type_, fields, relations, validate_only, bypass_rules,
                                  suppress_notifications,
                                  api_version)

        if with_links_and_attachments:
            wi.add_relations_raw(workitem.data.get('relations', {}), params)
        return wi


class TFSClientError(Exception):
    pass


class TFSHTTPClient:
    def __init__(self, base_url, project, user, password, pat, verify=False, timeout=None, auth_type=None):
        if not base_url.endswith('/'):
            base_url += '/'

        collection, project = self.get_collection_and_project(project)
        self.collection = collection
        self.project = project
        # Remove part after / in project-name, like DefaultCollection/MyProject => DefaultCollection
        # API responce only in Project, without subproject
        self._url = base_url + '%s/_apis/' % collection
        if project:
            self._url_prj = base_url + '%s/%s/_apis/' % (collection, project)
        else:
            self._url_prj = self._url

        self.http_session = requests.Session()
        if pat is not None:
            pat = ":" + pat
            pat_base64 = b'Basic ' + base64.b64encode(pat.encode("utf8"))
            self.http_session.headers.update({'Authorization': pat_base64})
        else:
            auth = auth_type() if user is None and password is None else auth_type(user, password)
            self.http_session.auth = auth

        self.api_version = None
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
        return self.__send_request('GET', uri, None, payload=payload, underProject=project, json=json)

    def send_post(self, uri, data, headers=None, payload=None, project=False):
        return self.__send_request('POST', uri, data, headers, payload=payload, underProject=project)

    def send_put(self, uri, data, headers=None, payload=None, project=False):
        return self.__send_request('PUT', uri, data, headers, payload=payload, underProject=project)

    def send_patch(self, uri, data, headers, payload=None, project=False):
        return self.__send_request('PATCH', uri, data, headers, payload=payload, underProject=project)

    def __send_request(self, method, uri, data, headers=None, payload=None, underProject=False, json=True):
        """
        Send request

        :param method:
        :param uri:
        :param data:
        :param headers:
        :param payload:
        :param underProject:
            False - add only collection to uri
            True - add Collection/Project to url, some api need it
            e.g. WIQL: https://www.visualstudio.com/en-us/docs/integrate/api/wit/wiql
        :param json:
            True - try to convert response to python-object
            False - get as is
        :return:
        """
        url = self.__prepare_uri(uri=uri, underProject=underProject)

        if payload is None:
            payload = {}
        if self.api_version and payload.get('api-version') is None:
            payload['api-version'] = self.api_version

        if headers is None:
            headers = {}
        if headers.get('Content-Type') is None:
            headers['Content-Type'] = 'application/json'

        if method == 'POST':
            response = self.http_session.post(url, json=data, verify=self._verify, headers=headers, params=payload,
                                              timeout=self.timeout)
        elif method == 'PUT':
            response = self.http_session.put(url, json=data, verify=self._verify, headers=headers, params=payload,
                                             timeout=self.timeout)
        elif method == 'PATCH':
            response = self.http_session.patch(url, json=data, verify=self._verify, headers=headers, params=payload,
                                               timeout=self.timeout)
        else:
            response = self.http_session.get(url, headers=headers, verify=self._verify, params=payload,
                                             timeout=self.timeout)
        response.raise_for_status()

        if self.api_version is None:
            api_type = response.headers['Content-Type'].split('; ')[-1].split('=')
            if api_type[0] == 'api-version':
                self.api_version = api_type[1]

        if json:
            try:
                result = response.json()

                if response.status_code != 200:
                    raise TFSClientError('TFS API returned HTTP %s (%s)' % (
                        response.status_code, result['error'] if 'error' in result else response.reason))
                return result
            except ValueError:
                raise TFSClientError('Response is not json: {}'.format(response.text))
        else:
            return response

    def __prepare_uri(self, underProject, uri):
        """
        Convert URI to URL

        :param underProject: if url need to have project name in it then True
        :param uri: relative uri or the full http url of the resource
        :return: full url to the resource
        """
        if uri.startswith('http'):
            # If we use URL (full path)
            url = uri
        else:
            # Add prefix to uri
            url = (self._url_prj if underProject else self._url) + uri
        return url
