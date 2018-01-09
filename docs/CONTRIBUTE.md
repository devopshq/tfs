# Table of Contents
- [Contribute](#contribute)
    - [Development](#development)
    - [Tests](#tests)

# Contribute
We will be grateful to see you in the ranks of the contributors! We have [some esay issue](https://github.com/devopshq/tfs/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22), which will suit as first issue or for junior python

## Development
Development takes place on GitHub, where the git-flow branch structure is used:

* ``master`` - contains the latest released code.
* ``develop`` - is used for development of the next release. **Pull request must be in this branch**
* ``feature/XXX`` - feature branches are used for development of new features before they are merged to ``develop``.

## Tests
We use HTTPPrety. For GET-response locate you response.json to folder by URL. E.g:
- http://tfs.tfs.ru/tfs/DefaultCollection/_apis/wit/workitems?ids=anyid&anyflag => **tests/resources/tfs/DefaultCollection/_apis/wit/workitems/response.json**
- http://tfs.tfs.ru/tfs/DefaultCollection/_apis/tfvc/changesets/10/workItems => **tests/resources/tfs/DefaultCollection/_apis/tfvc/changesets/10/workItems/response.json**
