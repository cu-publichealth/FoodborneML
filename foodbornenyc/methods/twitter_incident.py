"""
Twitter Incident Creator
"""

from datetime import timedelta, datetime
from time import time
from Queue import Queue

from foodbornenyc.sources.twitter.stream import stream, print_tweet_json
from foodbornenyc.sources.twitter.search import search
from foodbornenyc.sources.twitter.util import db, tweet_to_Tweet, get_logger

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

#search_terms = ['foodbornenyc']

class Incident():
    """ A data abstraction that keeps naive track of groups of tweets that might
    point at related pieces of info. Starting from a source tweet, an Incident
    will be able to backfill any tweets mentioning or from the author of that
    source tweet. This captures anything directed to the author, anything in
    the conversation tree of any tweet from the author. In addition, it takes
    tweets (from the streamer) and judges if those tweets should be added to
    it. """
    def __init__(self, source, timeframe=timedelta(days=7)):
        """ Create an incident from a source tweet """
        self.source = source
        self.tweets = [source]
        self.stray_tweets = []
        db.add(source)
        self.update_last_tweet_id()
        self.starttime = self.source.created_at or datetime.now()
        self.timeframe = timeframe

    def __repr__(self):
        return "<Incident(%s: %s)>" % (len(self.tweets), self.source)

    def active(self):
        return datetime.now() - self.starttime < self.timeframe

    def update_last_tweet_id(self):
        self.last_tweet_id = self.tweets[-1].id

    def backfill_tweets(self):
        """ Get all tweets from the author of the source tweet since the last
        time this method was called, adding them to the database. """
        name = self.source.user.screen_name
        new_tweets = search(['@'+name, 'from:'+name], self.last_tweet_id)
        if not new_tweets:
            return
        logger.info("Backfilling %s tweets for %s, last id %s"
                % (len(new_tweets), name, self.last_tweet_id))

        new_tweets = [db.merge(tweet_to_Tweet(t)) for t in new_tweets]
        new_ids = [t.id for t in new_tweets]
        stray = [db.merge(t) for t in self.stray_tweets if t.id not in new_ids]
        logger.info("%s other stray tweets" % len(stray))
        # doing the db.merge already added the tweets

        self.tweets.extend(stray)
        self.tweets.extend(new_tweets)
        self.update_last_tweet_id()
        self.stray_tweets = []
        logger.info("%s total tweets in %s" % (len(self.tweets), self))

    def offer_tweet(self, tweet):
        """ Possibly add a tweet to the incident, if it's relevant. Return
        whether or not the tweet was added. """
        if self.is_relevant_tweet(tweet):
            self.stray_tweets.append(tweet)
            return True
        return False

    def is_relevant_tweet(self, tweet):
        """ Determine if a tweet is relevant; that is, if it's in the timeframe
        and [in conversation with any of the current tweets or directly involves
        the source tweet's author]. """
        if tweet.created_at is not None:
            if abs(tweet.created_at - self.starttime) > self.timeframe:
                return False
        elif not self.active():
            return False

        # check if tweet is on source user's timeline or is retweet of source
        if (tweet.user.id == self.source.user.id or
                (tweet.in_reply_to and tweet.in_reply_to.user and
                tweet.in_reply_to.user.id == self.source.user.id) or
                (tweet.retweet_of and tweet.retweet_of.user and
                tweet.retweet_of.user.id == self.source.user.id)):
            return True

        # check if tweet is in the conversation tree
        for t in reversed(self.tweets):
            if tweet.in_reply_to and tweet.in_reply_to.id == t.id:
                return True

        return False


def incident_tweet(tweet):
    """ Classifier for if a tweet is worth creating an incident for. """
    return True
    # check if matching keywords
    # for kw in search_terms:
    #     if kw.replace('"', '') in tweet.text.lower():
    #         return True
    # return False

histo = [0]
def update_histo(oldlen, newlen):
    if len(histo) < newlen: histo.extend([0] * (newlen - len(histo)))
    if oldlen > 0: histo[oldlen-1] -= 1
    histo[newlen-1] += 1

def get_histo():
    return histo

last_search_time = 0
search_interval = 5
def receive_tweet(incidents, search_queue, tweet):
    """ Take a tweet and process it, possibly adding it to an incident or
    creating a new one out of it """
    global last_search_time, search_interval

    logger.info("Received %s" % tweet)
    # disregard retweets
    if (tweet.retweet_of is not None): return

    tweet = db.merge(tweet)
    offered = False
    first_inactive_inc = None

    for inc in reversed(incidents):
        # stop when we reach the inactive incidents. if a new incident has
        # become inactive since we last added a tweet, refresh the tracked users
        # this way depends on the incidents list being sorted by inactive time
        if not inc.active():
            if inc is not first_inactive_inc:
                first_inactive_inc = inc
            break

        # try to add the tweet to an incident.
        if inc.offer_tweet(tweet):
            logger.info("Found %s for %s" % (inc, tweet))
            # TODO: check if it's okay to just discard this tweet because
            # incidents will find the tweet themselves when they backfill
            offered = True
            newlen = len(inc.tweets) + len(inc.stray_tweets)
            update_histo(newlen-1, newlen)

    # make incidents for any tweets unrelated to current incidents
    if not offered and incident_tweet(tweet):
        inc = Incident(tweet)
        incidents.append(inc)
        update_histo(0, 1)
        search_queue.put(inc)
        logger.info("Created incident for %s" % tweet)

    # every search-interval seconds, backfill the oldest-updated incident
    if time() - last_search_time >= search_interval:
        next_incident = search_queue.get()
        logger.info("Doing backfill on %s" % next_incident)
        oldlen = len(next_incident.tweets) + len(next_incident.stray_tweets)
        next_incident.backfill_tweets()
        db.commit()
        newlen = len(next_incident.tweets) + len(next_incident.stray_tweets)
        update_histo(oldlen, newlen)
        if next_incident.active:
            search_queue.put(next_incident)
        last_search_time = time()
    logger.info("%s incidents: %s" % (len(incidents), get_histo()))

def track_incidents(incidents=[]):
    search_queue = Queue()
    def rec(tweet):
        receive_tweet(incidents, search_queue, tweet_to_Tweet(tweet))

    stream.set_function(rec)
    stream.keywords = set(search_terms)
    stream.start()
