# TODO

## General

- [ ] Unit Testing and `pytests`
- [ ] `pylint` for automated code reviews
- [ ] Consistent documentation
- [ ] Setup continuous integration with TravisCI
- [ ] Check that all used packages are under compatible licensing
- [ ] Decide what license we will want to use
- [ ] In the future: setup documentation with `Sphinx` and `ReadTheDocs`
- [ ] Use logging to file in deployment

## Twitter

- [ ] Search
- [ ] Robust API limit handling
    - This should probably be done through error handling since `twython` uses errors for api limits
- [ ] Streaming
- [ ] User location searching
- [ ] `Tweet` document class and schema
- [ ] `TwitterUser` class and schema
- [ ] Decide how to resolve `Location`s with bounding boxes
    - Possibly change schema to have optional `float` corners
- [ ] Tweet Classification class

## Yelp

- [x] Yelp Classification class
- [ ] Word embedding document classification

## User Interface

- [ ] Plan out a user interface

## Database

- [ ] Make seperate accounts and databases for Kevin and Steven