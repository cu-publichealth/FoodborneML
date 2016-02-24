import unittest
from mock import Mock, patch

import foodbornenyc.sources.twitter_search as twitter_search
from twython.exceptions import TwythonError

class TestTwitterSource(unittest.TestCase):
  def test_make_query(self):
    keywords = ['food', 'stomach', 'disease']
    statuses = [{'id_str':'2', 'text':"I hate food!"},\
                {'id_str':'34', 'text':"My stomach hurts..."}]
    tweets = {'statuses': statuses}

    twitter = Mock()
    twitter.search = Mock(return_value=tweets)

    query = twitter_search.make_query(twitter, keywords)

    twitter.search.assert_called_with(q='food OR stomach OR disease')
    self.assertEqual(query, statuses)

  def test_make_query_failed(self, logger):
    twitter = Mock()
    twitter.search = Mock(side_effect=TwythonError("Can't reach Twitter"))

    query = twitter_search.make_query(twitter, ['food'])

    self.assertEqual(query, [])
