# -*- coding: utf-8 -*-
"""
TFS API python 3 version
"""

from requests.structures import CaseInsensitiveDict

basestring = (str, bytes)


def cmp(a, b):
    return (a > b) - (a < b)


def to_str(a):
    return a.decode('utf-8') if isinstance(a, bytes) else str(a)


def to_bytes(a):
    return a.encode('utf-8') if isinstance(a, str) else a


class TFSObject(object):
    def __init__(self, data=None, tfs=None, uri=''):
        # TODO: CaseInsensitive Dict
        self._data = data
        self._attrib = self._data
        self.tfs = tfs
        self._attrib_prefix = ''
        self.id = self._data.get('id', None)
        self.uri = uri

    def __repr__(self):
        _repr = ''
        for k, v in self._attrib.items():
            _repr += to_str(k) + ' = ' + to_str(v) + '\n'
        return _repr

    def __iter__(self):
        for item in self._attrib:
            attr = self[item]
            if isinstance(attr, basestring) or isinstance(attr, list) \
                    or getattr(attr, '__iter__', False):
                yield item

    def get(self, key, default):
        if key in self._attrib:
            return self._attrib[key]
        key = self._add_prefix(key)
        return self._attrib.get(key, default)

    def __getitem__(self, key):
        if key in self._attrib:
            return self._attrib[key]

        key = self._add_prefix(key)
        return self._attrib[key]

    def __setitem__(self, key, value):
        if key in self._attrib:
            self._attrib[key] = value

        key = self._add_prefix(key)
        self._attrib[key] = value

    def _add_prefix(self, key):
        if key.startswith(self._attrib_prefix):
            return key
        else:
            return self._attrib_prefix + key

    def _remove_prefix(self, key):
        if key.startswith(self._attrib_prefix):
            return key[len(self._attrib_prefix):]
        else:
            return key


class Workitem(TFSObject):
    def __init__(self, data=None, tfs=None):
        super().__init__(data, tfs)
        self._attrib = CaseInsensitiveDict(self._data['fields'])
        self._attrib_prefix = 'System.'
        self.id = self._data['id']

    def __setitem__(self, key, value):
        field_path = "/fields/{}{}".format(self._attrib_prefix, key)
        update_data = [dict(op="add", path=field_path, value=value)]
        raw = self.tfs.update_workitem(self.id, update_data)
        self.__init__(raw, self.tfs)

    @property
    def field_names(self):
        return [self._remove_prefix(x) for x in self._attrib]

    @property
    def history(self):
        return self.tfs.get_tfs_object('wit/workitems/{}/history'.format(self.id))

    def _find_in_relation(self, relation_type, return_one=True):
        """
        Find relation type in relations and return one or list
        """
        ids = []
        for relation in self._data.get('relations', []):
            if relation_type in relation.get('rel', ''):
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


class Changeset(TFSObject):
    def __init__(self, data=None, tfs=None):
        super().__init__(data, tfs)
        self.id = self._data['changesetId']

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
    def __init__(self, data=None, tfs=None):
        super().__init__(data, tfs)
        self.result = self.tfs.rest_client.send_get('wit/wiql/{}?api-version=2.2'.format(self.id), project=True)
        self.columns = tuple(i['referenceName'] for i in self.result['columns'])
        self.column_names = tuple(i['name'] for i in self.result['columns'])
        self._workitems = None

    @property
    def workitems(self):
        if not self._workitems:
            self._workitems = self.tfs.get_workitems((i['id'] for i in self.result['workItems']))
        return self._workitems
