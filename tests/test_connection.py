# -*- coding: utf-8 -*-
import pytest

from tfs import *


@pytest.fixture()
def tfsapi():
    client = TFSAPI("http://tfs.tfs/tfs", 'Development', 'username', 'password')
    yield client


@pytest.mark.httpretty
def test_get_workitems(tfsapi):
    workitems = tfsapi.get_workitems(work_items_ids=[100, 101])

    assert len(workitems) == 2
    assert workitems[0].id == 100
    assert workitems[1].id == 101


@pytest.mark.httpretty
def test_get_workitem(tfsapi):
    workitem = tfsapi.get_workitem(100)

    assert isinstance(workitem, Workitem)
    assert workitem.id == 100


@pytest.mark.httpretty
def test_get_workitems_with_int(tfsapi):
    workitems = tfsapi.get_workitems(work_items_ids=100)

    assert len(workitems) == 2
    assert workitems[0].id == 100
    assert workitems[1].id == 101


@pytest.mark.httpretty
def test_get_changesets(tfsapi):
    changesets = tfsapi.get_changesets(from_=10, to_=14)

    assert len(changesets) == 5
    assert changesets[0].id == 10


@pytest.mark.httpretty
def test_get_changesets_workitem(tfsapi):
    changesets = tfsapi.get_changesets(from_=10, to_=14)
    changeset = changesets[0]
    workitems = changeset.workitems

    assert len(workitems) == 2
    assert workitems[0].id == 100
    assert workitems[1].id == 101


@pytest.mark.httpretty
def test_get_projects(tfsapi):
    projects = tfsapi.get_projects()

    assert len(projects) == 1
    assert projects[0]['name'] == 'ProjectName'


@pytest.mark.httpretty
def test_get_teams(tfsapi):
    projects = tfsapi.get_projects()
    team = projects[0].team

    assert isinstance(team, TFSObject)
    assert team['name'] == 'ProjectName'
