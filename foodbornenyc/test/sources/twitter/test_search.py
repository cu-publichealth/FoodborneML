import pytest
from mock import Mock, patch, call

import foodbornenyc.sources.twitter.search as search

from foodbornenyc.models.documents import Tweet
from foodbornenyc.test.test_db import clear_tables, get_db_session
from twython.exceptions import TwythonError

import foodbornenyc.test.sources.twitter.sample as sample

@patch('foodbornenyc.sources.twitter.search.twitter')
def test_search(twitter):
    """ The correct query should be requested """
    keywords = ['food', 'stomach', 'disease']
    tweets = {'statuses': sample.tweets}
    twitter.search = Mock(return_value=tweets)

    query = search.search(keywords)

    twitter.search.assert_called_with(count=100,\
                                      q='food OR stomach OR disease',\
                                      since_id=None)
    assert query == sample.tweets

@patch('foodbornenyc.sources.twitter.search.twitter')
def test_search_failed(twitter):
    """ If there's an exception, fail gracefully """
    twitter.search = Mock(side_effect=TwythonError("Can't reach Twitter"))

    query = search.search(['food'])

    assert query == []

@patch('foodbornenyc.sources.twitter.search.twitter')
# make query_twitter use the test db
@patch('foodbornenyc.sources.twitter.search.db', new_callable=get_db_session)
@patch('foodbornenyc.sources.twitter.search.time')
@patch('foodbornenyc.sources.twitter.search.sleep')
def test_query_twitter(sleep, time, db_session, twitter):
    """ Database should be filled with tweets returned from Twython """
    clear_tables()

    # make twitter return the sample tweets
    tweet_sequence = [{'statuses': [sample.tweets[0]]},
            {'statuses': [sample.tweets[1]]}]
    twitter.search = Mock(side_effect=tweet_sequence)

    # make time.time return canned values and time.sleep do nothing
    time_sequence = [5, 5, 10, 15]
    time.side_effect = time_sequence

    search.query_twitter(7, 5)

    assert len(time.call_args_list) == len(time_sequence)
    assert sleep.call_args_list == [call(5), call(5)]
    assert len(twitter.search.call_args_list) == 2
    sample.assert_matching_tweets(get_db_session().query(Tweet).all())
