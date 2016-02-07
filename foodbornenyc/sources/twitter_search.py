"""
Simple Twitter Search based on keywords once every 5 seconds and save to database
"""
import time

from twython import Twython

from foodbornenyc.models.documents import Tweet
from foodbornenyc.models.models import get_db_session

from foodbornenyc.db_settings import twitter_config

from foodbornenyc.util.util import sec_to_hms, get_logger
logger = get_logger(__name__, level="INFO")

def make_query(twitter, keywords):
    query = ' OR '.join(keywords)
    results = twitter.search(q=query)
    tweets = results['statuses']
    return tweets

def tweets_to_Tweets(tweet_list, select_fields):
    tweets = []
#     print select_fields
    for tweet in tweet_list:
        info = {k:v for (k,v) in tweet.items() if k in select_fields}
        tweets.append(Tweet(**info))
    return tweets

search_terms = [
    '#foodpoisoning',
    '#stomachache',
    '"food poison"',
    '"food poisoning"',
    'stomach',
    'vomit',
    'puke',
    'diarrhea',
    '"the runs"'
]

fields = [
#         'contributors', #<type 'NoneType'>
#         'truncated', #<type 'bool'>
        'text', #<type 'unicode'>
#         'is_quote_status', #<type 'bool'>
#         'in_reply_to_status_id', #<type 'NoneType'>
#         'id', #<type 'int'>
#         'favorite_count', #<type 'int'>
#         'source', #<type 'unicode'>
#         'retweeted', #<type 'bool'>
#         'coordinates', #<type 'NoneType'>
#         'entities', #<type 'dict'>
#         'in_reply_to_screen_name', #<type 'NoneType'>
#         'in_reply_to_user_id', #<type 'NoneType'>
#         'retweet_count', #<type 'int'>
        'id_str', #<type 'unicode'>
#         'favorited', #<type 'bool'>
        'user', #<type 'dict'>
#         'geo', #<type 'NoneType'>
        'in_reply_to_user_id_str', #<type 'NoneType'>
#         'possibly_sensitive', #<type 'bool'>
        'lang', #<type 'unicode'>
        'created_at', #<type 'unicode'>
        'in_reply_to_status_id_str', #<type 'NoneType'>
        'place', #<type 'NoneType'>
#         'metadata', #<type 'dict'>
         ]

def query_twitter(how_long=0):
    """ Inteface function """
    twitter = Twython(twitter_config['consumer_key'],
                      twitter_config['consumer_secret'],
                      twitter_config['access_token'],
                      twitter_config['access_token_secret'])
    db = get_db_session()
    # can send 180 requests per 15 min = 5 sec
    request_wait = 5
    start = time.time()
    id_set = set([ t.id for t in db.query(Tweet.id).all() ])
    # if we don't specify go indefinitely
    search_count = 0
    while not (how_long) or (time.time()-start < how_long):
        tweets = make_query(twitter, search_terms)
        logger.info("%i Total unique tweets in %i:%i:%i time", len(id_set), *sec_to_hms(time.time()-start))
        new_tweets = [ tweet for tweet in tweets if tweet['id_str'] not in id_set ]
        new_Tweets = tweets_to_Tweets(new_tweets, fields)
        id_set |= set([ t.id for t in new_Tweets ]) # union add all new ones
        db.add_all(new_Tweets)
        db.commit()
        time.sleep(request_wait)
