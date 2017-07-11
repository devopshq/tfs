### TFS Python Library (TFS API Python client).
## Quickstart
### Workitem get and update field
```python
from tfs import TFSAPI

user="username"
password="password"

client = TFSAPI("https://tfs.tfs.ru/tfs/", project="Development", user=user, password=password)
workitem = client.get_workitem(100)

# Case insensetive. Remove space in field name
print(workitem['assignedTo']) 

# Update field
workitem['state'] = 'Complete' 

# Add comment
workitem['History'] = "Omg, it is goos issue!"

print(workitem.history)

```
### Changesets and relation Workitem
```python
from tfs import TFSAPI

user="username"
password="password"

client = TFSAPI("https://tfs.tfs.ru/tfs/", project="Development", user=user, password=password)

# Get changesets from 1000 to 1002
changesets = client.get_changesets(from_=1000, to_=1002)

# Get changesets and related Workitems
changesets = client.get_changesets(top=1)
linked_workitems = changesets[0].workitems


```

## Installation
```
pip install dohq-tfs
```

## Guide
### Supported action:
- **Workitem**:
  - Get info about **Workitem**
  - Set field
- **Changeset**
  - Get info about **Changeset**
  - Get relation workitems

### Tested Compability:
- TFS 2015 

## Development
### Tests
We use HTTPPrety. For GET-response locate you response.json to folder by URL. E.g:
- http://tfs.tfs.rutfs/Development/_apis/wit/workitems?ids=anyid&anyflag => **tests/resources/tfs/Development/_apis/wit/workitems/response.json**
- http://tfs.tfs.rutfs/Development/_apis/tfvc/changesets/10/workItems => **tests/resources/tfs/Development/_apis/tfvc/changesets/10/workItems/response.json**

### TODO
- Implemented Resources-API (like https://github.com/pycontribs/jira)
