Examples
********

Create connection
=================

::

    from tfs import TFSAPI

    user="username"
    password="password"

    # Use DefaultCollection
    client = TFSAPI("https://tfs.tfs.ru/tfs/", user=user, password=password)

    # Use CustomCollection
    client = TFSAPI("https://tfs.tfs.ru/tfs/", project="DefaultCollection", user=user, password=password)

    # Set path to ProjectName in project parameter
    client = TFSAPI("https://tfs.tfs.ru/tfs/", project="DefaultCollection/ProjectName", user=user, password=password)

    workitem = client.get_workitem(100) # Test connection with Workitem id

Authorization
-------------

You can use password or `personal access token`__ in ``password`` field.

__ https://docs.microsoft.com/en-us/vsts/organizations/accounts/use-personal-access-tokens-to-authenticate?view=vsts

::

    # DEFAULT - Use HTTP Basic Auth
    client = TFSAPI("https://tfs.tfs.ru/tfs/", user=user, password=password)
    client = TFSAPI("https://tfs.tfs.ru/tfs/", user=user, password=personal_access_token)

    # Use NTLM authorization
    from requests_ntlm import HttpNtlmAuth

    client = TFSAPI("https://tfs.tfs.ru/tfs/", user=user, password=password, auth_type=HttpNtlmAuth)

    # Use HttpNegotiateAuth for single-sign-on with Kerberos
    # see more https://github.com/brandond/requests-negotiate-sspi
    import requests

    from requests_negotiate_sspi import HttpNegotiateAuth
    client = TFSAPI("https://tfs.tfs.ru/tfs/", auth_type=HttpNegotiateAuth)

Timeout connection
-------------------

You can set CONNECT and READ timeouts (`read more`__)

__ http://docs.python-requests.org/en/master/user/advanced/#timeouts

::

    from tfs import TFSAPI

    client = TFSAPI("https://tfs.tfs.ru/tfs/", user=user, password=password, connect_timeout=30, read_timeout=None)

.. _workitems:

Work Items
==========

::

    # For single Workitem
    workitem = client.get_workitem(100)

    # For multiple
    workitem = client.get_workitems([100,101,102]) # list
    workitem = client.get_workitems("100,101,102") # string separated with comma

    # Get all fields
    print(workitem.field_names)

    # Case insensetive. Remove space in field name
    print(workitem['assignedTo']) 

    # Workitem Parent Workitem
    parent = workitem.parent
    if parent: # Parent is None if Workitem hasn't Parent link
        print("Workitem with id={} have parent={}".format(workitem.id, parent.id))

    # Workitem Childs Workitem
    childs = workitem.childs
    if childs: # Child is empty list if Workitem hasn't Child link
        print("Workitem with id={} have Childs={}".format(workitem.id, ",".join([x.id for x in childs])))

    # Workitem revisions
    revisions = workitem.revisions

Create or copy workitem
-----------------------

::

    # Create new bug
    workitem = client.create_workitem('Bug')

    # Create new task with some fields (use field reference names, e.g. System.*)
    fields = {'System.Title': 'My task', 
            'System.Description': 'My description', 
            'System.AssignedTo': 'John Doe',
            'MyCompany.MyCustomField': 'MyCustomValue'}
    workitem = client.create_workitem('Task', fields=fields)

    # Copy with links and attachments and without sending notifications
    new_wi = client.copy_workitem(workitem, with_links_and_attachments=True, suppress_notifications=True)

.. _update-workitem:

Update workitem
---------------

::

    # Update field
    workitem['state'] = 'Complete' 

    # Add comment
    print(workitem.history)
    workitem['History'] = "Omg, it is a good issue!"
    print(workitem.history)

Workitem attachments
--------------------

If workitem has attachments, you can download it and get info about

::

    attachments = workitem.attachments
    attachment = attachments[0]
    # Internal TFS UID
    print(attachment.id) 

    # Filename
    print(attachment.name)

    # TFS Download URL
    print(attachment.url) 

    # You can download file to folder
    attachment.download('/home/user/folder') 

    # All raw data
    print(attachment.data)

.. _run-saved-queries:

Run Saved Queries
=================

You can run Saved Queries and get Workitems

::

    # Set path to ProjectName in project parameter
    client = TFSAPI("https://tfs.tfs.ru/tfs/", project="DefaultCollection/ProjectName", user=user, password=password)

    # Run New query 1 in Shared Queries folder
    query = client.run_query('Shared Queries/New query 1')
    # You can also use query GUID
    query = client.run_query('7d123e4af-f52e-4c0d-a220-b5cceffa8f5e')

    # result content raw data
    result = query.result
    print(query.columns)
    print(query.column_names)

    # Get all found workitems
    workitems = query.workitems

.. _run-wiql:

Run WIQL
========

You can run `Work Item Query Language`__

__ https://msdn.microsoft.com/en-us/library/bb130198(v=vs.90).aspx

::

    # Set path to ProjectName in project parameter
    client = TFSAPI("https://tfs.tfs.ru/tfs/", project="DefaultCollection/ProjectName", user=user, password=password)

    # Run custom query
    ### NOTE: Fields in SELECT really ignored, wiql return Work Items with all fields
    query = """SELECT
        [System.Id],
        [System.WorkItemType],
        [System.Title],
        [System.ChangedDate]
    FROM workitems
    WHERE
        [System.WorkItemType] = 'Bug'
    ORDER BY [System.ChangedDate]"""

    wiql = client.run_wiql(query)

    # Get found Work Item ids
    ids = wiql.workitem_ids
    print("Found WI with ids={}".format(",".join(ids)))

    # Get RAW query data - python dict
    raw = wiql.result

    # Get all found workitems
    workitems = wiql.workitems
    print(workitems[0]['Title'])

You can add extra `URI parameters`__ as a dictionary (only works for parameters
that come at the end of the link):

__ https://docs.microsoft.com/en-us/rest/api/vsts/wit/wiql/query%20by%20wiql?view=vsts-rest-4.1#uri-parameters

::

    wiql = client.run_query(query, params={'$top': 10, 'timePrecision': True, 'api-version': '1.0'})
