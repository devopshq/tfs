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
attachments = workitem1.find_in_relation('AttachedFile')
for attachment in attachments:
    workitem2.add_relation(attachment)
```

## Links
Some `TFSObject` have `_links` in their data. You can acces to this data as raw or get new `TFSObject`:
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
**TODO**: Describe how other people can use some usefull function and object from `tfs.connection`
- Get from TFSAPI
- `send_*` methods
