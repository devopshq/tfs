import os
from urllib.parse import urlparse

import httpretty
import pytest


def request_callback(request, uri, headers):
    # Map path from url to a file
    parsed_url = urlparse(uri)
    response_file = os.path.normpath('tests/resources%s' % parsed_url.path)
    response_file = os.path.join(response_file, 'response.json')

    if os.path.exists(response_file):
        code = 200
        response = open(response_file, mode='r', encoding="utf-8-sig").read()
    else:
        code = 404
        response = "{}"

    return code, headers, response


@pytest.fixture(autouse=True)
def tfs_server_mock():
    import re
    httpretty.register_uri(httpretty.GET, re.compile(r"http://tfs.tfs/tfs/(.*)"),
                           body=request_callback,
                           content_type="application/json")
