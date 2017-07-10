import pytest

from tfs import TFSAPI


@pytest.fixture()
def tfsapi():
    client = TFSAPI("http://tfs.tfs/tfs", 'Development', 'username', 'password')
    yield client


@pytest.mark.httpretty
def test_get_workitems(tfsapi):
    workitems = tfsapi.get_workitems(work_items_ids=[1370, 1371])

    assert len(workitems) == 2
    assert workitems[0].id == 100
    assert workitems[1].id == 101


@pytest.mark.httpretty
def test_get_workitems_with_int(tfsapi):
    workitems = tfsapi.get_workitems(work_items_ids=1370)

    assert len(workitems) == 2
    assert workitems[0].id == 100
    assert workitems[1].id == 101


@pytest.mark.httpretty
def test_get_changesets(tfsapi):
    changesets = tfsapi.get_changesets(From=10, to=14)

    assert len(changesets) == 5
    assert changesets[0].id == 10


@pytest.mark.httpretty
def test_get_changesets_workitem(tfsapi):
    changesets = tfsapi.get_changesets(From=10, to=14)
    changeset = changesets[0]
    workitems = changeset.get_workitems()

    assert len(workitems) == 2
    assert workitems[0].id == 100
    assert workitems[1].id == 101
