"""
Wrapper module for a Twitter stream that can add/remove users and terms to track
"""

from twython import TwythonStreamer, TwythonError
from time import time, sleep
from foodbornenyc.db_settings import twitter_config
from foodbornenyc.util.util import get_logger

logger = get_logger(__name__, level="INFO")

def streamer_config(args):
    """ convert Twython config dict to TwythonStreamer config """
    return {'app_key': args['consumer_key'],
            'app_secret': args['consumer_secret'],
            'oauth_token': args['access_token'],
            'oauth_token_secret': args['access_token_secret']}

def print_tweet_json(tweet):
    print "%s\n%s\n" % (tweet['user']['name'],tweet['text'])

class FoodBorneStreamer(TwythonStreamer):
    def __init__(self, *args, **kwargs):
        TwythonStreamer.__init__(self, *args, **streamer_config(kwargs))
        self.counter = 0
        self.count_limit = 0
        self.error_counter = 0
        self.error_limit = 1000
        self.users = set()
        self.keywords = set()
        self.receive_tweet = print_tweet_json

    def on_success(self, data):
        self.counter += 1
        try:
            if 'text' not in data:
                logger.warning("Empty tweet %s" % data)
                return
            self.receive_tweet(data)
        except TwythonError as e:
            logger.error("Twython Error: %s" % e)

    def on_error(self, status_code, data):
        logger.warning( "Twitter Error status code: %s" % status_code)
        self.error_counter += 1
        if str(status_code) == "420": 
            logger.info("Rate Limited: waiting a minute")
            sleep(60)

    def update_filter(self):
        self.statuses.set_dynamic_filter(follow=','.join(self.users),
                                         track=','.join(self.keywords))
    def set_function(self, func):
        self.receive_tweet = func

    def start(self):
        self.update_filter()
        if self.users or self.keywords:
            self.statuses.dynamic_filter()
        else:
            logger.error("Can't start stream with no keywords or users")

stream = FoodBorneStreamer(**twitter_config)

