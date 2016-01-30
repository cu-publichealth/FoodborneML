# FoodborneNYC

The new implementation of a system to mine social media documents for evidence of foodborne illness outbreaks in NYC restaurants.

This software will be used by the NYC Department of Health and Mental Hygiene (DOHMH) to inform their practices.

It is intended to eventually serve as boilerplate for other municipal agencies wishing to leverage social media for actionable inference in practice.

Currently it's just research code.

## For Readers of the code / those just looking over the project


## For Developers of the code


### Best Practice References

- We will be following (as closely as possible) the style guide for python specified in [PEP #0008](https://www.python.org/dev/peps/pep-0008/)
- We will be using [Sphinx](http://www.sphinx-doc.org/en/stable/) to autogenerate documentation from the code.
    - It will be available on ReadTheDocs (link to come)
- We will be following git team best practices(links to come).  This means branching, merging, rebasing 
   - Before merging a branch, **document what you have!**

- We will be following Hitchhikers guide to python closely
- We will be using Jenkinz for continuous integration (or emaybe TravisCI)
- We will be writing unit tests using `pytests`
- We will be using pylint to help with code reviews  (automated code analysis)
- We must make sure every dependency is licensed in a compatible way
- We must choose our LICENSE and create a license.txt file

- A useful reference [Writing idomatic python](https://www.jeffknupp.com/writing-idiomatic-python-ebook/)

- Oooh this looks very helpful [guide to open sourcing a python project](https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/)



### TODO

A high level list of todo's can be kept here.

1. Twitter streaming and search
    - Tweet data model for DB
    - API limit handling
    - Robust error handling
    - Tracking conversations
2. User Interface
    - Probably a simple flask server with access to the DB through the ```models```
    - For use by DOHMH so we can better present results and collect the data in a way that works best for the system and classification models.
3. Integration Services and Unit Testing
4. Documentation (always, always, always)
5. Improve document level classification (always, always, always)
6. 

