# -*- coding: utf-8 -*-
import json

import pytest

from tfs.tfs import Workitem


@pytest.fixture()
def workitem():
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


def test_workitem_id(workitem):
    assert workitem.id == 1370


def test_workitem_fields(workitem):
    assert workitem['Reason'] == "New"
    assert workitem['AreaPath'] == "Test Agile"


def test_workitem_fields_with_prefix(workitem):
    assert workitem['System.Reason'] == "New"
    assert workitem['System.AreaPath'] == "Test Agile"


def test_workitem_fields_case_ins(workitem):
    assert workitem['ReaSon'] == "New"
    assert workitem['AREAPath'] == "Test Agile"
