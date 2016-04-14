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
    newargs = args.copy()
    newargs['app_key'] = newargs.pop('consumer_key')
    newargs['app_secret'] = newargs.pop('consumer_secret')
    newargs['oauth_token'] = newargs.pop('access_token')
    newargs['oauth_token_secret'] = newargs.pop('access_token_secret')
    return newargs

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

stream = FoodBorneStreamer(**twitter_config)

def set_stream_function(func):
    streamer.receive_tweet = func

def track_users(*new_users):
    stream.users |= set(new_users)
    stream.update_filter()

def untrack_users(*users_to_remove):
    stream.users -= set(users_to_remove)
    stream.update_filter()

def track_keywords(*new_keywords):
    stream.keywords |= set(new_keywords)
    stream.update_filter()

def untrack_keywords(*keywords_to_remove):
    stream.keywords -= set(new_keywords)
    stream.update_filter()

def start_stream():
    stream.update_filter()
    if stream.users or stream.keywords:
        stream.statuses.dynamic_filter()
    else:
        logger.error("Can't start stream with no keywords or users")

def stop_stream():
    stream.disconnect()
