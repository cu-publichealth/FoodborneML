"""
Simple Twitter Search based on keywords once every 5 seconds & save to database
"""
from time import time, sleep

from twython import Twython
from twython.exceptions import TwythonError
from sqlalchemy.exc import OperationalError

from foodbornenyc.models.documents import Tweet
from foodbornenyc.db_settings import twitter_config
from foodbornenyc.sources.twitter.util \
    import tweet_to_Tweet, user_to_TwitterUser, place_to_Location,\
           reset_location_cache, twitter, db

from foodbornenyc.util.util import sec_to_hms, get_logger, xuni
logger = get_logger(__name__, level="INFO")


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

def search(keywords, since_id=None, count=100):
    """ Take keywords and Twython object and return back the statuses"""
    query = ' OR '.join(keywords)
    try:
        results = twitter.search(q=query, since_id=since_id, count=count)
        tweets = results['statuses']
    except TwythonError as e:
        logger.warning("Twython Error for query '%s'" % query)
        tweets = []
    return tweets

def query_twitter(how_long=0, interval=5):
    """ Interface function """
    reset_location_cache()
    # can send 180 requests per 15 min = 5 sec
    start = time()

    # make sure we don't create duplicates.
    # keeping track of this ourselves saves many db hits
    # if we don't specify go indefinitely
    last_tweet_id = 0
    while time() - start < how_long:
        tweets = search(search_terms, last_tweet_id)
        if not tweets: # if we dont get anything back, sleep and try again
            sleep(interval)
            continue
        # if a retrieved tweet has a loc/user with a matching ID already in the
        # db, that loc/user is updated instead of a new one added, bc of merge
        try:
            db.add_all([db.merge(tweet_to_Tweet(t)) for t in tweets])
            db.commit()
            last_tweet_id = tweets[0]['id_str']
        except OperationalError:
            pass
        sleep(interval)

