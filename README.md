TFS Python Library (TFS API Python client)
==========================================
- [Quickstart](#quickstart)
    - [Installation](#installation)
    - [Create connection](#create-connection)
    - [Workitem](#workitem)
    - [Run Queries](#run-queries)
    - [Changesets](#changesets)
    - [Project and Team](#project--team)
- [Guide](#guide)
    - [Compability](#compability)
    - [Development](#development)
        - [Tests](#tests)
        - [TODO](#todo)

# Quickstart
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
client = TFSAPI("https://tfs.tfs.ru/tfs/", project="Development", user=user, password=password)

# Set path to ProjectName in project parameter
client = TFSAPI("https://tfs.tfs.ru/tfs/", project="Development/ProjectName", user=user, password=password)

workitem = client.get_workitem(100) # Test connection with Workitem id
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

# Update field
workitem['state'] = 'Complete' 

# Add comment
print(workitem.history)
workitem['History'] = "Omg, it is goos issue!"
print(workitem.history)

# Workitem Parent Workitem
parent = workitem.parent
if parent: # Parent is None if Workitem hasn't Parent link
    print("Workitem with id={} have parent={}".format(workitem.id, parent.id))

# Workitem Childs Workitem
childs = workitem.childs
if childs: # Child is empty list if Workitem hasn't Child link
    print("Workitem with id={} have Childs={}".format(workitem.id, ",".join([x.id for x in childs])))
```

## Run Queries
You can run Saved Queries and get Workitems
```python
# Set path to ProjectName in project parameter
client = TFSAPI("https://tfs.tfs.ru/tfs/", project="Development/ProjectName", user=user, password=password)

# Run New query 1 in Shared Queries folder
quiery = client.run_query('Shared Queries/New query 1')

# result content raw data
result = quiery.result
print(quiery.columns)
print(quiery.column_names)

# Get all found workitems
workitems = quiery.workitems
```

## Changesets
```python
# Get changesets from 1000 to 1002
changesets = client.get_changesets(from_=1000, to_=1002)

# Get changesets and related Workitems
changesets = client.get_changesets(top=1)
linked_workitems = changesets[0].workitems
```

## Project & Team
```python
# Get all project
all_projects = client.get_projects()

# Get project
project_name = client.get_project("MyProjectName")

# Get project team
project_team = project_name.team
```


## Guide
### Compability
- TFS 2015 
- TFS 2017

## Development
### Tests
We use HTTPPrety. For GET-response locate you response.json to folder by URL. E.g:
- http://tfs.tfs.ru/tfs/Development/_apis/wit/workitems?ids=anyid&anyflag => **tests/resources/tfs/Development/_apis/wit/workitems/response.json**
- http://tfs.tfs.ru/tfs/Development/_apis/tfvc/changesets/10/workItems => **tests/resources/tfs/Development/_apis/tfvc/changesets/10/workItems/response.json**

### TODO
- Implemented Resources-API (like https://github.com/pycontribs/jira)
