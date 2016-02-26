import unittest
from mock import Mock

import foodbornenyc.sources.twitter_search as twitter_search
from foodbornenyc.util.util import xuni
from foodbornenyc.models.documents import Tweet
from twython.exceptions import TwythonError

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
            'place': None
        }]

class TestTwitterSource(unittest.TestCase):

    def test_make_query(self):
        """ Test a sample query """
        keywords = ['food', 'stomach', 'disease']
        tweets = {'statuses': sample}

        twitter = Mock()
        twitter.search = Mock(return_value=tweets)

        query = twitter_search.make_query(twitter, keywords)

        twitter.search.assert_called_with(q='food OR stomach OR disease')
        self.assertEqual(query, sample)

    def test_make_query_failed(self):
        """ Make Query should fail gracefully """
        twitter = Mock()
        twitter.search = Mock(side_effect=TwythonError("Can't reach Twitter"))

        query = twitter_search.make_query(twitter, ['food'])

        self.assertEqual(query, [])

    def test_tweets_to_Tweets(self):
        """ Convert sample tweets """
        fields = ['text', 'id_str']
        tweets = twitter_search.tweets_to_Tweets(sample, fields)

        self.assertEqual(len(tweets), 2)
        self.assertEqual(tweets[0].text, sample[0]['text'])
        self.assertEqual(tweets[0].id, sample[0]['id_str'])
        self.assertEqual(tweets[1].text, sample[1]['text'])
        self.assertEqual(tweets[1].id, sample[1]['id_str'])


