Microsoft TFS Python Library (TFS API Python client)
==========================================

[![docs](https://img.shields.io/readthedocs/pip.svg)](https://devopshq.github.io/tfs/)  [![dohq-tfs build status](https://travis-ci.org/devopshq/tfs.svg)](https://travis-ci.org/devopshq/tfs) [![dohq-tfs code quality](https://api.codacy.com/project/badge/Grade/a533e2d46b9b471893b4991e89649212)](https://www.codacy.com/app/tim55667757/tfs/dashboard) [![dohq-tfs code coverage](https://api.codacy.com/project/badge/Coverage/a533e2d46b9b471893b4991e89649212)](https://www.codacy.com/app/tim55667757/tfs/dashboard) [![dohq-tfs on PyPI](https://img.shields.io/pypi/v/dohq-tfs.svg)](https://pypi.python.org/pypi/dohq-tfs) [![dohq-tfs license](https://img.shields.io/pypi/l/vspheretools.svg)](https://github.com/devopshq/tfs/blob/master/LICENSE)

------

# Table of Contents
- [Introduction](#introduction)
- [Quickstart](#quickstart)
    - [Installation](#installation)
    - [Create connection](#create-connection)
        - [Authorization](#authorization)
        - [Timeout connection](#timeout-connection)
    - [Workitem](#workitem)
        - [Create or copy workitem](#create-or-copy-workitem)
        - [Update workitem](#update-workitem)
        - [Workitem attachments](#workitem-attachments)
    - [Run Saved Queries](#run-saved-queries)
    - [Run WIQL](#run-wiql)
    - [Advanced](#advanced)
- [Troubleshooting](#troubleshooting)
- [Guide](#guide)
    - [Compatibility](#Compatibility)
    - [Contribute](#contribute)

------

# Introduction
Microsoft Team Foundation Server Python Library is a Microsoft TFS API Python client that can work with Microsoft TFS workflow and workitems.

This python library allows:
1. Get [WorkItems (WI)](#workitem)
2. Set [WI fields](#update-workitem)
3. Run [WI search queries](#run-saved-queries)
4. Run [WIQL](#run-wiql)
4. Work [with TFVC changesets](docs/OTHER.md)
5. Work [with TFS Projects](docs/OTHER.md)

## Installation
```
pip install dohq-tfs
```

## Create connection
```python
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
```

### Authorization
You can use password or [personal access token](https://docs.microsoft.com/en-us/vsts/organizations/accounts/use-personal-access-tokens-to-authenticate?view=vsts) in `password` field.
```python
# DEFAULT - Use HTTP Basic Auth
client = TFSAPI("https://tfs.tfs.ru/tfs/", user=user, password=password)
client = TFSAPI("https://tfs.tfs.ru/tfs/", user=user, password=personal_access_token)

# Use NTLM authorization
from requests_ntlm import HttpNtlmAuth
client = TFSAPI("https://tfs.tfs.ru/tfs/", user=user, password=password, auth_type=HttpNtlmAuth)

```

## Timeout connection
You can set CONNECT and READ timeouts ([read more](http://docs.python-requests.org/en/master/user/advanced/#timeouts))
```python
from tfs import TFSAPI
client = TFSAPI("https://tfs.tfs.ru/tfs/", user=user, password=password, connect_timeout=30, read_timeout=None)
```

## Workitem
```python
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
```
### Create or copy workitem
```python
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
```

### Update workitem

```python
# Update field
workitem['state'] = 'Complete' 

# Add comment
print(workitem.history)
workitem['History'] = "Omg, it is a good issue!"
print(workitem.history)
```

### Workitem attachments
If workitem has attachments, you can download it and get info about.
```python
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
```

## Run Saved Queries
You can run Saved Queries and get Workitems
```python
# Set path to ProjectName in project parameter
client = TFSAPI("https://tfs.tfs.ru/tfs/", project="DefaultCollection/ProjectName", user=user, password=password)

# Run New query 1 in Shared Queries folder
quiery = client.run_query('Shared Queries/New query 1')

# result content raw data
result = quiery.result
print(quiery.columns)
print(quiery.column_names)

# Get all found workitems
workitems = quiery.workitems
```

## Run WIQL
You can run [Work Item Query Language](https://msdn.microsoft.com/en-us/library/bb130198(v=vs.90).aspx)
```python
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
```

You can add extra [URI parameters](https://docs.microsoft.com/en-us/rest/api/vsts/wit/wiql/query%20by%20wiql?view=vsts-rest-4.1#uri-parameters) as a dictionary (only works for parameters that come at the end of the link):
```python
wiql = client.run_query(query, params={'$top': 10, 'timePrecision': True, 'api-version': '1.0'})
```

## Advanced
- [Advanced usage](docs/ADVANCED.md)
- Some [other objects available](docs/OTHERS.md)

# Troubleshooting

If you cannot create or update a work item, here are some possible reasons:
- check if the account you use has **enough permissions** in the collection/project;
- make sure you **follow your workflow**, work items might have required fields or any other sort of restrictions;
- verify that the api version [fits your team foundation server version](https://docs.microsoft.com/en-us/vsts/integrate/concepts/rest-api-versioning);

If neither of these helped your case, [look through our issues list](https://github.com/devopshq/tfs/issues).
If there is no similar issue, [create one](https://github.com/devopshq/tfs/issues/new).

# Guide
If you use this library, [put a star](https://help.github.com/articles/about-stars/) on [this repository](https://github.com/devopshq/tfs). This motivates us and other developers to develop the library :)

## Compatibility
- Tested with **Python.3.4**
- TFS 2015 
- TFS 2017

## Contribute
[About contribute](docs/CONTRIBUTE.md)
