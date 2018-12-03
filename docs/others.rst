.. _other_usages:

Other usages
************

.. _tfs-changesets:

Changesets
==========

::

    # Get changesets from 1000 to 1002
    changesets = client.get_changesets(from_=1000, to_=1002)

    # Get just a particular changeset
    changeset = client.get_changeset(1000)

    # Get changesets and related Workitems
    changesets = client.get_changesets(top=1)
    linked_workitems = changesets[0].workitems

.. _tfs-projects:

Project & Team
==============

::

    # Get all project
    all_projects = client.get_projects()

    # Get project
    project_name = client.get_project("MyProjectName")

    # Get project team
    project_team = project_name.team
