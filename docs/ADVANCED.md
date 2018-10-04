Advanced usage
--------------

# Table of Contents
- [TFSObject](#tfsobject)
- [Workitem](#workitem)
    - [Relations](#relations)
    - [Links](#links)
- [TFSHTTPClient](#tfshttpclient)

# TFSObject
All `TFSObject` instances contain raw TFS response (in JSON, which was converted to python-dict) in `self.data`

```python
workitem = client.get_workitem(100)
print(workitem.data)

history = workitem.history
print(history.data)

revisions = workitem.revisions
print(revisions.data)

attachment = workitem.attachments[0]
print(attachment.data)
```

All `TFSObject` instances have `self.url`, `self.uri`:
```python
workitem = client.get_workitem(100)

# Full URL with https points to API object
print(workitem.url)

# URI points to API object
print(workitem.uri)

```

# Workitem

## Relations
Workitem has relation with other object. This library support only `workitem.childs`, `workitem.parent`, and `workitem.attachments`
Read more about [TFS link types](https://docs.microsoft.com/en-us/vsts/work/customize/reference/link-type-element-reference#link-types)

If you need find other type, you can use `workitem.find_in_relations` method:
```python
workitem = client.get_workitem(100)

# links is Dict
links = workitem.find_in_relation('Hyperlink') 

# duplicates is Dict
# Really type is System.LinkTypes.Duplicate-Forward, but it will be found
duplicates = workitem.find_in_relation('Duplicate-Forward') 
```

Existing relations (links, attachments) can be added to another work item:
```python
attachments_raw = workitem1.find_in_relation('AttachedFile')
workitem2.add_relations_raw(attachments_raw)
```

## Links
Some `TFSObject` have `_links` in their data. You can access to this data as raw or get new `TFSObject`:
```python
workitem = client.get_workitem(100)

# This links also in dir()
dir(workitem)

# Get TFSObject
workitem.workItemHistory # list of object
workitem.workItemRevisions # list of object
workitem.workItemType # TFSObject

# Get raw data
links = workitem.data['_links']
print(links)

```

## TFSHTTPClient
If you want full control over contents of your requests, you can use `rest_client` to send raw request via `send_get`, `send_post` and `send_patch` methods:

```python
client = TFSAPI(...)
new_task_raw = client.rest_client.send_post(
    uri,        # short address: '/_apis/wit/workitems/$task'
                # or full address: 'https://<full_web_path_to_tfs_collection>/<project>/_apis/wit/workitems/$task'
    data,       # request body, e.g. 
#[
#  {
#    "op": "add",
#    "path": "/fields/System.Title",
#    "from": null,
#    "value": "Sample task"
#  }
#]
    verify,     # SSL verification (see docs for Python Requests at http://docs.python-requests.org/en/master/user/advanced/#ssl-cert-verification) 
    headers,    # request headers, e.g. {'Content-Type': 'application/json-patch+json'}
    payload,    # url parameters, e.g. {'validateOnly': True, 'api-version': '1.0', 'whatever': 'whatnot'}
                # these will be appended to resulting URL as parameters (?validateOnly=true&api-version=1.0&whatever=whatnot)
    project     # set to True for project-related API (e.g. work item creation)
)

new_task = WorkItem(client, new_task_raw)
```  

The `send_patch` method has the same parameters as `send_post` while `send_get` does not use `data` as GET-requests naturally do not have body.