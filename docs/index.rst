Microsoft TFS Python Library (TFS API Python client)
####################################################

|build status| |docs| |code quality| |code coverage| |pypi| |license|

.. toctree::
    :hidden:

    installation
    examples
    advanced
    others
    contribution
    api
    GitHub <https://github.com/devopshq/tfs>

Introduction
************

Microsoft Team Foundation Server Python Library is a Microsoft TFS API Python client
that can work with Microsoft TFS workflow and workitems.

Quick Start
***********

This python library allows:

#. Get :ref:`work Items (WI) <workitems>`
#. Set :ref:`WI fields <update-workitem>`
#. Run :ref:`WI search queries <run-saved-queries>`
#. Run :ref:`WIQL <run-wiql>`
#. Work with :ref:`TFVC changesets <tfs-changesets>`
#. Work with :ref:`TFS Projects <tfs-projects>`
#. :ref:`Advanced usage <advanced>` - what is :py:class:`tfs.TFSObject`,
   find and add with Workitem relations,
   links, and information about :py:class:`tfs.TFSHTTPClient`
#. Some :ref:`other objects available <other_usages>` -
   :py:class:`tfs.Changeset`, :py:class:`tfs.Project`, :py:class:`tfs.Team`,
   :py:class:`tfs.Workitem`

Troubleshooting
***************

If you cannot create or update a work item, here are some possible reasons:

* check if the account you use has **enough permissions** in the collection/project
* make sure you **follow your workflow**, work items might have required fields
  or any other sort of restrictions
* verify that the api version `fits your team foundation server version`__

__ https://docs.microsoft.com/en-us/vsts/integrate/concepts/rest-api-versioning

If neither of these helped your case - `look through our issues list`__.

__ https://github.com/devopshq/tfs/issues

If there is no similar issue - `create one`__.

__ https://github.com/devopshq/tfs/issues/new

Guide
*****

If you use this library, `put a star`__ on `this repository`__.
This motivates us and other developers to develop the library :)

__ https://help.github.com/articles/about-stars/
__ https://github.com/devopshq/tfs

Compatibility
*************

* Tested with **Python.3.4**
* TFS 2015 
* TFS 2017

Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |build status| image:: https://travis-ci.org/devopshq/tfs.svg
    :alt: Build Status
    :scale: 100%
    :target: https://travis-ci.org/devopshq/tfs
.. |docs| image:: https://img.shields.io/readthedocs/pip.svg
    :alt: Documentation Status
    :scale: 100%
    :target: https://devopshq.github.io/tfs/
.. |code quality| image:: https://api.codacy.com/project/badge/Grade/a533e2d46b9b471893b4991e89649212
    :alt: Code Quality
    :target: https://www.codacy.com/app/tim55667757/tfs/dashboard
.. |code coverage| image:: https://api.codacy.com/project/badge/Coverage/a533e2d46b9b471893b4991e89649212
    :alt: Code Quality
    :target: https://www.codacy.com/app/tim55667757/tfs/dashboard
.. |pypi| image:: https://img.shields.io/pypi/v/dohq-tfs.svg
    :alt: PyPI
    :target: https://pypi.python.org/pypi/dohq-tfs
.. |license| image:: https://img.shields.io/pypi/l/vspheretools.svg
    :alt: License
    :target: https://github.com/devopshq/tfs/blob/master/LICENSE
