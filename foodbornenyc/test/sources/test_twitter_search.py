import pytest
from mock import Mock, patch, call

import foodbornenyc.sources.twitter_search as twitter_search

from foodbornenyc.models.documents import Tweet
from foodbornenyc.test.test_db import clear_tables, get_db_session
from twython.exceptions import TwythonError

place1 = {'id': '12345'}
place2 = {'id': '23456',
          'attributes': {'street_address': '1234 Broadway'},
          'country': 'United States',
          "bounding_box": { "coordinates": [[
              [-1, -1],
              [1, -1],
              [1, 1],
              [-1, 1]]],
              "type": "Polygon"},
          }

sample = [ {
            'id_str':'2',
            'text':"I hate food!",
            'user': {'id_str': '234'},
            'in_reply_to_user_id_str': None,
            'lang': 'en',
            'created_at': 'Tue Feb 23 23:40:54 +0000 2015',
            'in_reply_to_status_id_str': None,
            'place': None
        }, {
            'id_str':'34',
            'text':"My stomach hurts!",
            'user': {'id_str': '2234'},
            'in_reply_to_user_id_str': None,
            'lang': 'en',
            'created_at': 'Tue Feb 23 21:00:11 +0000 2015',
            'in_reply_to_status_id_str': None,
            'place': place2
        }]

def test_make_query():
    """ The correct query should be requested """
    keywords = ['food', 'stomach', 'disease']
    tweets = {'statuses': sample}

    twitter = Mock()
    twitter.search = Mock(return_value=tweets)

    query = twitter_search.make_query(twitter, keywords)

    twitter.search.assert_called_with(q='food OR stomach OR disease')
    assert query == sample

def test_make_query_failed():
    """ If there's an exception, fail gracefully """
    twitter = Mock()
    twitter.search = Mock(side_effect=TwythonError("Can't reach Twitter"))

    query = twitter_search.make_query(twitter, ['food'])

    assert query == []

def test_tweets_to_Tweets():
    """ Sample tweets should be converted properly """
    fields = ['text', 'id_str', 'place']
    tweets = twitter_search.tweets_to_Tweets(sample, fields)
    assert_matching_tweets(tweets)

def test_location_from_place():
    assert twitter_search.location_from_place(None) == None

    location1 = twitter_search.location_from_place(place1)
    assert location1.line1 == ''
    assert location1.country == ''
    assert location1.street_address == place1['id']

    location2 = twitter_search.location_from_place(place2)
    assert location2.street_address == place2['id']
    assert location2.line1 == place2['attributes']['street_address']
    assert location2.country == place2['country']
    assert location2.longitude == 0
    assert location2.latitude == 0
    assert location2.bbox_width == 2
    assert location2.bbox_height == 2

@patch('foodbornenyc.sources.twitter_search.Twython')
@patch('foodbornenyc.sources.twitter_search.get_db_session')
@patch('foodbornenyc.sources.twitter_search.time')
@patch('foodbornenyc.sources.twitter_search.sleep')
def test_query_twitter(sleep, time, db_session, twython):
    """ Database should be filled with tweets returned from Twython """
    clear_tables()

    # make twitter return the sample tweets
    tweet_sequence = [{'statuses': [sample[0]]}, {'statuses': [sample[1]]}]
    twitter = twython.return_value
    twitter.search = Mock(side_effect=tweet_sequence)

    # make get_db_session in query_twitter use the test db
    db_session.return_value = get_db_session()

    # make time.time return canned values and time.sleep do nothing
    time_sequence = [5, 5, 10, 15]
    time.side_effect = time_sequence

    twitter_search.query_twitter(7, 5)

    assert len(time.call_args_list) == len(time_sequence)
    assert sleep.call_args_list == [call(5), call(5)]
    assert len(twitter.search.call_args_list) == 2
    assert_matching_tweets(get_db_session().query(Tweet).all())

def assert_matching_tweets(tweets):
    """ Helper method for checking if tweets match sample """
    assert len(tweets) == 2
    assert tweets[0].text == sample[0]['text']
    assert tweets[0].id == sample[0]['id_str']
    assert tweets[1].text == sample[1]['text']
    assert tweets[1].id == sample[1]['id_str']
    assert tweets[1].location.line1 == place2['attributes']['street_address']


