Contribution
************

We will be grateful to see you in the ranks of the contributors!
We have `some easy issue`__, which will suit as first issue or for junior python.

__ https://github.com/devopshq/tfs/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22

Development
===========

Development takes place on GitHub, where the git-flow branch structure is used:

* ``master`` - contains the latest released code
* ``develop`` - is used for development of the next release. **Pull request must be in this branch**
* ``feature/XXX`` - feature branches are used for development of new features
    before they are merged to ``develop``

Documentation
=============

We use sphinx to build docs::

    cd docs-sphinx
    make html
    # open ./docs/_build/html/index.html on your browser
    start ./_build/html/index.html # Windows


Publish
~~~~~~~~~~~~~~

For repositories admin:

  + All documentation saved in ``docs``-folder on branches.
  + We use ``gh-pages`` as source for publishing on github pages.
  + Read example how it work on `habr.com (Russian) <https://habr.com/post/180213/>`__

Run this script to publish new html on https://devopshq.github.io/tfs/ ::

    cd docs
    bash ./publish-gh-pages.sh


Tests
=====

We use the HTTP client mocking tool `HTTPPretty <https://github.com/gabrielfalcao/HTTPretty>`__.

For GET-response locate you response.json to folder by URL. E.g:

* http://tfs.tfs.ru/tfs/DefaultCollection/_apis/wit/workitems?ids=anyid&anyflag
    => **tests/resources/tfs/DefaultCollection/_apis/wit/workitems/response.json**
* http://tfs.tfs.ru/tfs/DefaultCollection/_apis/tfvc/changesets/10/workItems
    => **tests/resources/tfs/DefaultCollection/_apis/tfvc/changesets/10/workItems/response.json**
