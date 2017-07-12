TFS Python Library (TFS API Python client)
==========================================

[links]

*Index:*
- [Quickstart](#Chapter_1)
    - [Create connection](#Chapter_1_1)
        - [Workitem](#Chapter_1_1_1)
        - [Changesets](#Chapter_1_1_2)
        - [Project and Team](#Chapter_1_1_3)
    - [Installation](#Chapter_1_2)
    - [Guide](#Chapter_1_3)
        - [Tested compability](#Chapter_1_3_1)
    - [Development](#Chapter_1_4)
        - [Tests](#Chapter_1_4_1)
        - [TODO](#Chapter_1_4_2)


# Quickstart <a name="Chapter_1"></a>


## Create connection <a name="Chapter_1_1"></a>

    from tfs import TFSAPI
    
    user="username"
    password="password"
    
    client = TFSAPI("https://tfs.tfs.ru/tfs/", project="Development", user=user, password=password)
    workitem = client.get_workitem(100) # Test connection with Workitem id


### Workitem <a name="Chapter_1_1_1"></a>

    workitem = client.get_workitem(100)
    
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


### Changesets <a name="Chapter_1_1_2"></a>

    # Get changesets from 1000 to 1002
    changesets = client.get_changesets(from_=1000, to_=1002)
    
    # Get changesets and related Workitems
    changesets = client.get_changesets(top=1)
    linked_workitems = changesets[0].workitems


### Project and Team <a name="Chapter_1_1_3"></a>

    # Get all project
    all_projects = client.get_projects()
    
    # Get project
    project_name = client.get_project("MyProjectName")
    
    # Get project team
    project_team = project_name.team


## Installation <a name="Chapter_1_2"></a>

    pip install dohq-tfs


## Guide <a name="Chapter_1_3"></a>


### Tested compability <a name="Chapter_1_3_1"></a>

- TFS 2015 


## Development <a name="Chapter_1_4"></a>


### Tests <a name="Chapter_1_4_1"></a>

We use HTTPPrety. For GET-response locate you response.json to folder by URL. E.g:
- http://tfs.tfs.ru/tfs/Development/_apis/wit/workitems?ids=anyid&anyflag => **tests/resources/tfs/Development/_apis/wit/workitems/response.json**
- http://tfs.tfs.ru/tfs/Development/_apis/tfvc/changesets/10/workItems => **tests/resources/tfs/Development/_apis/tfvc/changesets/10/workItems/response.json**


### TODO <a name="Chapter_1_4_2"></a>
- Implemented Resources-API (like https://github.com/pycontribs/jira)
