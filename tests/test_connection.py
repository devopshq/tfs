# -*- coding: utf-8 -*-
import pytest

from tfs import *


class TestTFSAPI:
    @pytest.mark.httpretty
    def test_get_workitems(self, tfsapi):
        workitems = tfsapi.get_workitems(work_items_ids=[100, 101])

        assert len(workitems) == 2
        assert workitems[0].id == 100
        assert workitems[1].id == 101

    @pytest.mark.httpretty
    def test_get_workitem(self, tfsapi):
        workitem = tfsapi.get_workitem(100)

        assert isinstance(workitem, Workitem)
        assert workitem.id == 100

    @pytest.mark.httpretty
    def test_get_workitems_with_int(self, tfsapi):
        workitems = tfsapi.get_workitems(work_items_ids=100)

        assert len(workitems) == 2
        assert workitems[0].id == 100
        assert workitems[1].id == 101

    @pytest.mark.httpretty
    def test_get_changesets(self, tfsapi):
        changesets = tfsapi.get_changesets(from_=10, to_=14)

        assert len(changesets) == 5
        assert changesets[0].id == 10

    @pytest.mark.httpretty
    def test_get_projects(self, tfsapi):
        projects = tfsapi.get_projects()

        assert len(projects) == 1
        assert projects[0]['name'] == 'ProjectName'

    @pytest.mark.httpretty
    def test_get_project(self, tfsapi):
        projects = tfsapi.get_project('ProjectName')

        assert len(projects) == 1
        assert projects[0]['name'] == 'ProjectName'

    @pytest.mark.httpretty
    def test_get_teams(self, tfsapi):
        projects = tfsapi.get_projects()
        team = projects[0].team

        assert isinstance(team, TFSObject)
        assert team['name'] == 'ProjectName'

    class TestHTTPClient:
        def test__get_collection(self):
            collection, project = TFSHTTPClient.get_collection_and_project('Development')
            assert collection == 'Development'
            assert project is None

        def test__get_collection_and_project(self):
            collection, project = TFSHTTPClient.get_collection_and_project('Development/Project')
            assert collection == 'Development'
            assert project == 'Project'

        def test__get_collection_and_project_and_team(self):
            collection, project = TFSHTTPClient.get_collection_and_project('Development/Project/Team')
            assert collection == 'Development'
            assert project == 'Project'
