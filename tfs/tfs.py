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
        key = self._add_prefix(key)
        return self._attrib.get(key, default)

    def __getitem__(self, key):
        key = self._add_prefix(key)
        return self._attrib[key]

    def __setitem__(self, key, value):
        key = self._add_prefix(key)
        self._attrib[key] = value

    def _add_prefix(self, key):
        if self._attrib_prefix:
            return self._attrib_prefix + key
        return key

        # def __getattribute__(self, item):
        #     if item in self._data:
        #         return self._data[item]
        #
        #     return object.__getattribute__(self, item)


class Workitem(TFSObject):
    def __init__(self, data=None, tfs=None):
        super().__init__(data, tfs)
        self._attrib = CaseInsensitiveDict(self._data['fields'])
        self._attrib_prefix = 'System.'
        self.id = self._data['id']

    def __setitem__(self, key, value):
        field_path = "/fields/{}{}".format(self._attrib_prefix, key)
        update_data = [dict(op="add", path=field_path, value=value)]
        self = self.tfs.update_workitem(self.id, update_data)

    @property
    def history(self):
        return self.tfs.get_tfs_object('wit/workitems/{}/history'.format(self.id))


class Changeset(TFSObject):
    def __init__(self, data=None, tfs=None):
        super().__init__(data, tfs)
        self.id = self._data['changesetId']

    @property
    def workitems(self):
        """
        :param changeset_id:
        :return:
        """
        wi_links = self.tfs.get_tfs_object('tfvc/changesets/{}/workItems'.format(self.id))
        ids = [x.id for x in wi_links]
        workitems = self.tfs.get_workitems(ids)
        return workitems


class Projects(TFSObject):
    @property
    def team(self):
        return self.tfs.get_tfs_object('projects/{}/teams'.format(self.id))
