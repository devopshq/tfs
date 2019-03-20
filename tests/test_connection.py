# -*- coding: utf-8 -*-
import pytest
import httpretty
import re

from tfs import *
from tests.conftest import request_callback_get


class TestTFSAPI:
    @httpretty.activate
    def test_get_gitrepositories_with_pat(self):
        def request_callback_get_pat(request, uri, headers):
            authorization = request.headers.get('Authorization')
            assert authorization == "Basic OmtsNWt0bnR3M2V6dnh0aGl0YzVhZTR1YmdzZWRpMnFrcWh6cWNuZ2hnNzV0azJuNHJnZmE="

            code, headers, response = request_callback_get(request, uri, headers)
            return code, headers, response

        httpretty.register_uri(httpretty.GET, re.compile(r"http://tfs.tfs.ru(.*)"),
                               body=request_callback_get_pat)

        client = TFSAPI("http://tfs.tfs.ru/tfs", 'DefaultCollection',
                        pat='kl5ktntw3ezvxthitc5ae4ubgsedi2qkqhzqcnghg75tk2n4rgfa')

        repos = client.get_gitrepositories()
        name = repos[0].data['name']
        assert name == 'AnotherRepository'\

    @httpretty.activate
    def test_get_gitrepositories_with_pat_and_password(self):
        # if pat and password are given then it is expected that the password is ignored and the pat header is added
        def request_callback_get_pat(request, uri, headers):
            authorization = request.headers.get('Authorization')
            assert authorization == "Basic OmtsNWt0bnR3M2V6dnh0aGl0YzVhZTR1YmdzZWRpMnFrcWh6cWNuZ2hnNzV0azJuNHJnZmE="

            code, headers, response = request_callback_get(request, uri, headers)
            return code, headers, response

        httpretty.register_uri(httpretty.GET, re.compile(r"http://tfs.tfs.ru(.*)"),
                               body=request_callback_get_pat)

        client = TFSAPI("http://tfs.tfs.ru/tfs", 'DefaultCollection', user='any_user', password='any_password',
                        pat='kl5ktntw3ezvxthitc5ae4ubgsedi2qkqhzqcnghg75tk2n4rgfa')

        repos = client.get_gitrepositories()
        name = repos[0].data['name']
        assert name == 'AnotherRepository'

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
        workitems = tfsapi.get_workitems(work_items_ids=[100,101])

        assert len(workitems) == 2
        assert workitems[0].id == 100
        assert workitems[1].id == 101

    @pytest.mark.httpretty
    def test_get_changesets(self, tfsapi):
        changesets = tfsapi.get_changesets(from_=10, to_=14)

        assert len(changesets) == 5
        assert changesets[0].id == 10

    @pytest.mark.httpretty
    def test_get_changeset(self, tfsapi):
        changeset = tfsapi.get_changeset(10)

        assert changeset.id == 10

    @pytest.mark.httpretty
    def test_run_query(self, tfsapi):
        query = tfsapi.run_query('My Queries/AssignedToMe')

        assert isinstance(query, TFSQuery)
        assert isinstance(query.result, Wiql)
        assert query.name == 'AssignedToMe'
        assert query.path == 'My Queries/AssignedToMe'

    @pytest.mark.httpretty
    def test_get_wiql(self, tfsapi):
        wiql_query = "SELECT *"
        wiql = tfsapi.run_wiql(wiql_query)

        assert isinstance(wiql, Wiql)
        assert wiql.workitem_ids == [100, 101]

    @pytest.mark.httpretty
    def test_get_projects(self, tfsapi):
        projects = tfsapi.get_projects()

        assert len(projects) == 1
        assert projects[0]['name'] == 'ProjectName'

    @pytest.mark.httpretty
    def test_projects(self, tfsapi):
        projects = tfsapi.projects

        assert len(projects) == 1
        assert projects[0]['name'] == 'ProjectName'

    @pytest.mark.httpretty
    def test_get_project(self, tfsapi):
        project = tfsapi.get_project('ProjectName')

        assert project.name == 'ProjectName'

    @pytest.mark.httpretty
    def test_project(self, tfsapi):
        project = tfsapi.project('ProjectName')

        assert project.name == 'ProjectName'

    @pytest.mark.httpretty
    def test_get_teams(self, tfsapi):
        projects = tfsapi.projects
        teams = projects[0].teams

        assert isinstance(teams[0], Team)
        assert teams[1]['name'] == 'TeamPink'

    @pytest.mark.httpretty
    def test_get_gitrepositories(self, tfsapi):
        repos = tfsapi.get_gitrepositories()
        name = repos[0].data['name']

        assert name == 'AnotherRepository'

    @pytest.mark.httpretty
    def test_get_gitrepository(self, tfsapi):
        repo = tfsapi.get_gitrepository('AnotherRepository')
        name = repo.data['name']

        assert name == 'AnotherRepository'

    @pytest.mark.httpretty
    def test_adjusted_area_iteration(self):
        new_project = 'NewProject'
        api = TFSAPI("http://tfs.tfs.ru/tfs", 'DefaultCollection/{}'.format(new_project), 'username', 'password')

        old_area = 'OldProject\\Area1'
        new_area = '{}\\Area1'.format(new_project)

        assert api._TFSAPI__adjusted_area_iteration(old_area) == new_area


class TestHTTPClient:
    def test__get_collection(self):
        collection, project = TFSHTTPClient.get_collection_and_project('DefaultCollection')
        assert collection == 'DefaultCollection'
        assert project is None

    def test__get_collection_and_project(self):
        collection, project = TFSHTTPClient.get_collection_and_project('DefaultCollection/Project')
        assert collection == 'DefaultCollection'
        assert project == 'Project'

    def test__get_collection_and_project_and_team(self):
        collection, project = TFSHTTPClient.get_collection_and_project('DefaultCollection/Project/Team')
        assert collection == 'DefaultCollection'
        assert project == 'Project'
