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
    will request certain users to be tracked and accept later tweets deemed
    relevant to this incident. An incident will ultimately consist in a source
    tweet, the user's timeline going back and forward a specified period of
    time, and all the tweets in the timeframe in conversation with the timeline
    tweets. """
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
        # get all new tweets from the author of the source
        # commit those tweets and any tweets offered to this incident from the
        # streamer to the db
        name = self.source.user.screen_name
        query = ['@'+name, 'from:'+name]
        new_tweets = search(query, self.last_tweet_id)
        if not new_tweets:
            return
        logger.info("Backfilling %s tweets having %s, last id %s"
                % (len(new_tweets), query, self.last_tweet_id))

        new_tweets = [db.merge(tweet_to_Tweet(t)) for t in new_tweets]
        other_stray = [t for t in self.stray_tweets if t not in new_tweets]
        logger.info("%s other stray tweets" % len(other_stray))
        db.add_all(other_stray)
        db.add_all(new_tweets)
        db.commit()

        self.tweets.extend(other_stray)
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

        # check if tweet is on source user's timeline
        if (tweet.user.id == self.source.user.id or
                (tweet.in_reply_to and tweet.in_reply_to.user and
                tweet.in_reply_to.user.id == self.source.user.id)):
            return True

        # check if tweet is in the conversation tree
        for t in reversed(self.tweets):
            if tweet.in_reply_to and tweet.in_reply_to.id == t.id:
                return True

        return False


def incident_tweet(tweet):
    """ Classifier for if a tweet is worth creating an incident for. """
    # currently checks if matches keywords
    for kw in search_terms:
        if kw.replace('"', '') in tweet.text.lower():
            return True

    return False

last_search_time = 0
search_interval = 5
def receive_tweet(incidents, search_queue, tweet):
    """ Take a tweet and process it, possibly adding it to an incident or
    creating a new one out of it """
    global last_search_time, search_interval

    tweet = db.merge(tweet)
    logger.info("Received tweet %s" % tweet)
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

        # try to add the tweet to an incident. if added and it brings a new user
        # to the table, prepare to update the tracked users list
        if inc.offer_tweet(tweet):
            logger.info("Found incident %s for %s" % (inc, tweet))
            # TODO: check if it's okay to just discard this tweet because
            # incidents will find the tweet themselves when they backfill
            offered = True

    if not offered and incident_tweet(tweet):
        inc = Incident(tweet)
        incidents.append(inc)
        search_queue.put(inc)
        logger.info("Created incident for %s" % tweet)

    if time() - last_search_time >= search_interval:
        # update tweets on the oldest-updated incident
        next_incident = search_queue.get()
        logger.info("Doing backfill on %s" % next_incident)
        next_incident.backfill_tweets()
        if next_incident.active:
            search_queue.put(next_incident)
        last_search_time = time()
    # print [str(len(i.tweets)) + " " + str(len(i.users)) for i in incidents]
    logger.info("%s incidents total" % len(incidents))

def track_incidents():
    incidents = []
    search_queue = Queue()
    def rec(tweet):
        receive_tweet(incidents, search_queue, tweet_to_Tweet(tweet))

    stream.set_function(rec)
    stream.keywords = set(search_terms)
    stream.start()
