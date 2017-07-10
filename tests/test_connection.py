import pytest

from tfs import TFSAPI


@pytest.mark.httpretty
def test_get_workitems():
    client = TFSAPI("http://tfs.tfs/tfs", 'Development', 'username', 'password')
    workitems = client.get_workitems(work_items_ids=[1370, 1371])
    assert len(workitems) == 2
    assert workitems[0].id == 1370
    assert workitems[1].id == 1371
