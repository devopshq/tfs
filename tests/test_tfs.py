# -*- coding: utf-8 -*-
import json

import pytest

from tfs.tfs import *


class TestWorkitem(object):
    @pytest.fixture()
    def workitem(self):
        data_str = r"""{
            "id": 1370,
            "rev": 1,
            "fields": {
                "System.AreaPath": "Test Agile",
                "System.TeamProject": "Test Agile",
                "System.IterationPath": "Test Agile\\Current\\Iteration 1",
                "System.WorkItemType": "Bug",
                "System.State": "Active",
                "System.Reason": "New",
                "System.CreatedDate": "2015-10-14T07:40:46.96Z",
                "System.CreatedBy": "Alexey Ivanov <DOMAIN\\AIvanov>",
                "System.ChangedDate": "2015-10-14T07:40:46.96Z",
                "System.ChangedBy": "Alexey Ivanov <DOMAIN\\AIvanov>",
                "System.Title": "\u044c\u0441\u0440\u0442\u043e",
                "Microsoft.VSTS.Common.StateChangeDate": "2015-10-14T07:40:46.96Z",
                "Microsoft.VSTS.Common.ActivatedDate": "2015-10-14T07:40:46.96Z",
                "Microsoft.VSTS.Common.ActivatedBy": "Alexey Ivanov <DOMAIN\\AIvanov>",
                "Microsoft.VSTS.Common.Priority": 2,
                "Microsoft.VSTS.Common.Severity": "3 - Medium"
            },
            "url": "https:\/\/tfs.tfs.ru\/tfs\/Development\/_apis\/wit\/workItems\/1370"
        }"""
        data_ = json.loads(data_str)
        wi = Workitem(data_)
        yield wi

    def test_workitem_id(self, workitem):
        assert workitem.id == 1370

    def test_workitem_fields(self, workitem):
        assert workitem['Reason'] == "New"
        assert workitem['AreaPath'] == "Test Agile"

    def test_workitem_fields_with_prefix(self, workitem):
        assert workitem['System.Reason'] == "New"
        assert workitem['System.AreaPath'] == "Test Agile"

    def test_workitem_fields_case_ins(self, workitem):
        assert workitem['ReaSon'] == "New"
        assert workitem['AREAPath'] == "Test Agile"


class TestChangeset(object):
    @pytest.fixture()
    def changeset(self):
        data_str = r"""{
          "changesetId": 10,
          "url": "https:\/\/tfs.tfs.ru\/tfs\/Development\/_apis\/tfvc\/changesets\/18736",
          "author": {
            "id": "831299d4-f278-4858-a188-d1edae64125d",
            "displayName": "\u041c\u0438\u0445\u0430\u0438\u043b \u041f\u043e\u043b\u044c\u0433\u0443\u043d",
            "uniqueName": "DOMAIN\\MIvanov",
            "url": "https:\/\/tfs.tfs.ru\/tfs\/Development\/_apis\/Identities\/831299d4-f278-4858-a188-d1edae64125d",
            "imageUrl": "https:\/\/tfs.tfs.ru\/tfs\/Development\/_api\/_common\/identityImage?id=831299d4-f278-4858-a188-d1edae64125d"
          },
          "checkedInBy": {
            "id": "dc115031-b185-421e-a58d-b2b19903f51a",
            "displayName": "deploy",
            "uniqueName": "DOMAIN\\deploy",
            "url": "https:\/\/tfs.tfs.ru\/tfs\/Development\/_apis\/Identities\/dc115031-b185-421e-a58d-b2b19903f51a",
            "imageUrl": "https:\/\/tfs.tfs.ru\/tfs\/Development\/_api\/_common\/identityImage?id=dc115031-b185-421e-a58d-b2b19903f51a"
          },
          "createdDate": "2017-06-30T15:43:41.71Z",
          "comment": "My Comment"
        }"""
        data_ = json.loads(data_str)
        cs = Changeset(data_)
        yield cs

    def test_changeset_id(self, changeset):
        assert changeset.id == 10

    def test_changeset_fields(self, changeset):
        assert changeset['comment'] == "My Comment"

    @pytest.mark.httpretty
    def test_get_changesets_workitem(self, tfsapi):
        changesets = tfsapi.get_changesets(from_=10, to_=14)
        changeset = changesets[0]
        workitems = changeset.workitems

        assert len(workitems) == 2
        assert workitems[0].id == 100
        assert workitems[1].id == 101
