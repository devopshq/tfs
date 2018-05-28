# -*- coding: utf-8 -*-
"""
TFS API python 3 version
"""
import os

from copy import deepcopy
from requests.structures import CaseInsensitiveDict


class TFSObject(object):
    def __init__(self, data=None, tfs=None, uri=''):
        # TODO: CaseInsensitive Dict

        self.data = data
        self.tfs = tfs
        self.id = self.data.get('id', None)
        self.uri = uri
        self.url = self.data['url'] if 'url' in self.data else None

        self._data = self.data  # legacy, some people can use private method

    def __dir__(self):
        """
        Extend standart dir() with attribute in `_links`
        :return: extended list of attribute name
        """
        original = super(TFSObject, self).__dir__()
        extend = self.data.get('_links', {})
        extend = list(extend)
        new_dir = original + extend
        return new_dir

    def __get_object_by_links(self, name):
        """
        Dynamically add property for all ``_links`` field in JSON, if exist
        """
        links = self.data.get('_links', {})  # or emtpy if _links is not exist
        url = links[name]['href']
        return self.tfs.get_tfs_object(url)

    def __getattr__(self, name):
        """
        If object have not attribute, try search in `_links` and return new TFSObject
        :param name:
        :return: TFSObject
        """
        if name in self.data.get('_links', {}):
            return self.__get_object_by_links(name)
        raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name))

    # TODO: implement better repr
    # def __repr__(self):
    #     _repr = ''
    #     for k, v in self.data.items():
    #         _repr += to_str(k) + ' = ' + to_str(v) + '\n'
    #     return _repr

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        """
        We not implement default behavior, use class for it
        :param key:
        :param value:
        :return:
        """
        raise NotImplemented

    def get(self, key, default=None):
        return self.data.get(key, default)


class Workitem(TFSObject):
    def __init__(self, data=None, tfs=None, uri=''):
        super().__init__(data, tfs, uri)

        # Use prefix in automatically lookup.
        # We don't need use wi['System.History'], we use simple wi['History']
        self._system_prefix = 'System.'

        self.id = self.data['id']
        self.fields = CaseInsensitiveDict(self.data['fields'])
        self._fields = self.fields

    def __setitem__(self, key, value):
        field_path = "/fields/{}".format(key)
        update_data = [dict(op="add", path=field_path, value=value)]
        raw = self.tfs.update_workitem(self.id, update_data)
        self.__init__(raw, self.tfs)

    def get(self, key, default=None):
        if key in self.fields:
            return self.fields[key]

        # try to automatically add prefix
        key = self._add_prefix(key)
        return self.fields.get(key, default)

    def __getitem__(self, key):
        if key in self.fields:
            return self.fields[key]

        # try to automatically add prefix
        key = self._add_prefix(key)
        return self.fields[key]

    def _add_prefix(self, key):
        if key.startswith(self._system_prefix):
            return key
        else:
            return self._system_prefix + key

    def _remove_prefix(self, key):
        if key.startswith(self._system_prefix):
            return key[len(self._system_prefix):]
        else:
            return key

    @property
    def field_names(self):
        return [self._remove_prefix(x) for x in self.fields]

    @property
    def history(self):
        return self.workItemHistory

    @property
    def revisions(self):
        return self.workItemRevisions

    def find_in_relation(self, relation_type):
        """
        Get relation by type\name. Auto add
        :param relation_type:
        :return:
        """
        found = []
        for relation in self.data.get('relations', []):
            # Find as is, e.g. 'AttachedFile' or more smartly.
            # Found 'Hierarchy-Forward' in 'System.LinkTypes.Hierarchy-Forward'
            if relation_type == relation.get('rel', '') \
                    or relation.get('rel', '').endswith(relation_type):
                found.append(relation)
        return found

    def _find_in_relation(self, relation_type, return_one=True):
        """
        Find relation type in relations and return one or list
        one use for Parent WI
        """
        ids = []
        relations = self.find_in_relation(relation_type)
        for relation in relations:
            id_ = relation['url'].split('/')[-1]
            id_ = int(id_)
            ids.append(id_)
        if return_one:
            return ids[0] if ids else None
        else:
            return ids

    @property
    def parent_id(self):
        return self._find_in_relation('Hierarchy-Reverse', return_one=True)

    @property
    def parent(self):
        if self.parent_id is None:
            return None
        return self.tfs.get_workitem(self.parent_id)

    @property
    def child_ids(self):
        return self._find_in_relation('Hierarchy-Forward', return_one=False)

    @property
    def childs(self):
        if self.child_ids:
            return self.tfs.get_workitems(self.child_ids)
        else:
            return []

    @property
    def attachments(self):
        list_ = self.find_in_relation('AttachedFile')
        attachments_ = [Attachment(x, self.tfs) for x in list_]
        return attachments_

    def add_relations_raw(self, relations_raw):
        """
        Add attachments, related (work item) links and/or hyperlinks
        :param relations_raw: List of relations. Each relation is a dict with the following keys: rel, url, attributes
        """
        # remove ID from attributes as it has to be unique
        copy_raw = [deepcopy(relation) for relation in relations_raw]
        for relation in copy_raw:
            if 'attributes' in relation:
                if 'id' in relation['attributes']:
                    del relation['attributes']['id']

        path = '/relations/-'
        update_data = [dict(op="add", path=path, value=relation) for relation in copy_raw]
        if update_data:
            raw = self.tfs.update_workitem(self.id, update_data)
            self.__init__(raw, self.tfs)


class Attachment(TFSObject):
    def __init__(self, data=None, tfs=None, uri=''):
        super().__init__(data, tfs, uri)
        self.id = self.data['url'].split('/')[-1]  # Get UUID from url
        self.name = self.data['attributes']['name']

    def download(self, path='.'):
        path = os.path.join(path, self.name)
        self.tfs.download_file(self.url, path)


class Changeset(TFSObject):
    def __init__(self, data=None, tfs=None, uri=''):
        super().__init__(data, tfs, uri)
        self.id = self.data['changesetId']

    @property
    def workitems(self):
        wi_links = self.tfs.get_tfs_object('tfvc/changesets/{}/workItems'.format(self.id))
        ids = [x.id for x in wi_links]
        workitems = self.tfs.get_workitems(ids)
        return workitems


class Projects(TFSObject):
    @property
    def team(self):
        return self.tfs.get_tfs_object('projects/{}/teams'.format(self.id))


class TFSQuery(TFSObject):
    def __init__(self, data=None, tfs=None, uri=''):
        super().__init__(data, tfs, uri)
        self.result = self.tfs.rest_client.send_get('wit/wiql/{}?api-version=2.2'.format(self.id), project=True)
        self.columns = tuple(i['referenceName'] for i in self.result['columns'])
        self.column_names = tuple(i['name'] for i in self.result['columns'])
        self._workitems = None

    @property
    def workitems(self):
        if not self._workitems:
            self._workitems = self.tfs.get_workitems((i['id'] for i in self.result['workItems']))
        return self._workitems


class Wiql(TFSObject):
    """
    Work Item Query Language
    """

    def __init__(self, data=None, tfs=None, uri=''):
        super().__init__(data, tfs, uri)
        self.result = self.data

    @property
    def workitem_ids(self):
        ids = [x['id'] for x in self.data['workItems']]
        return ids

    @property
    def workitems(self):
        return self.tfs.get_workitems(self.workitem_ids)


class GitRepository(TFSObject):
    pass
