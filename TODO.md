# TODO

## General

- [ ] Unit Testing and `pytests`
- [ ] `pylint` for automated code reviews
- [ ] Consistent documentation
- [ ] Setup continuous integration with TravisCI
- [ ] Check that all used packages are under compatible licensing
- [ ] Decide what license we will want to use
- [ ] In the future: setup documentation with `Sphinx` and `ReadTheDocs`
- [ ] Event-based logging piped to file in deployment

## Twitter

- [x] `Tweet` document class and schema
- [ ] `TwitterUser` class and schema
- [ ] Decide how to resolve `Location`s with bounding boxes
    - Possibly change schema to have optional `float` corners
- [ ] Tweet Classification class
- [ ] Search
- [ ] Verify Twitter search gets similar feed as Java version
- [ ] Verify that it picks up my test tweets
- [ ] Robust API limit handling
    - This should probably be done through error handling since `twython` uses errors for api limits
- [ ] Streaming
- [ ] Location search strategies
    - [ ] User location
    - [ ] Past Tweet locations going back some amount (maybe one month) and some threshold (percentage or count)
    - [ ] Locations of followers/following? Probably unreliable
- [ ] Context gathering
    - [ ] User timelines
    - [ ] Urls in tweets
    - [ ] Follow conversations
- [ ] Expanding keywords used in search/stream query
    - Using topic modeling
    - Using query growth strategy from Hila


## Yelp

- [x] Yelp Classification class
- [ ] Word embedding document classification

## User Interface

- [ ] Plan out a user interface

## Database

- [ ] Make seperate accounts and databases for Kevin and Steven
