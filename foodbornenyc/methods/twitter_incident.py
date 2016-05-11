"""
Twitter Incident Creator
"""

from foodbornenyc.sources.twitter.stream import stream, print_tweet_json
from foodbornenyc.sources.twitter.util import db, tweet_to_Tweet
from datetime import timedelta, datetime

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
        self.users = {self.source.user.id}

        self.starttime = self.source.created_at or datetime.now()
        self.timeframe = timeframe

    def __repr__(self):
        return "<Incident(%s: %s)>" % (len(self.tweets), self.source)

    def active(self):
        return datetime.now() - self.starttime < self.timeframe

    def users_to_track(self):
        """ A list of users for a streamer updating this incident to track. """
        if self.active():
            return self.users
        return None

    def offer_tweet(self, tweet):
        """ Possibly add a tweet to the incident, if it's relevant. Return
        whether or not the tweet was added. """
        if self.is_relevant_tweet(tweet):
            self.tweets.append(tweet)
            self.users.add(tweet.user.id)
            if tweet.in_reply_to and tweet.in_reply_to.user:
                self.users.add(tweet.in_reply_to.user.id)
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

histo = [0]
def receive_tweet(incidents, tweet):
    """ Take a tweet and process it, possibly adding it to an incident or
    creating a new one out of it """
    global histo, maxlen
    tweet = db.merge(tweet)
    print "Received tweet " + str(tweet)
    offered = False
    outdated_users = False
    first_inactive_inc = None

    for inc in reversed(incidents):
        # stop when we reach the inactive incidents. if a new incident has
        # become inactive since we last added a tweet, refresh the tracked users
        # this way depends on the incidents list being sorted by inactive time
        if not inc.active():
            if inc != first_inactive_inc:
                first_inactive_inc = inc
                outdated_users = True
            break

        # try to add the tweet to an incident. if added and it brings a new user
        # to the table, prepare to update the tracked users list
        if inc.offer_tweet(tweet):
            print "Found incident for tweet"
            offered = True
            newlen = len(inc.tweets)
            if len(histo) < newlen:
                histo.append(0)
            histo[newlen-2] -= 1
            histo[newlen-1] += 1
            if (tweet.user.id not in stream.users or (
                    tweet.in_reply_to and tweet.in_reply_to.user and 
                    tweet.in_reply_to.user.id not in stream.users)):
                outdated_users = True

    if offered:
        db.add(tweet)
    elif incident_tweet(tweet):
        print "Created incident for tweet"
        db.add(tweet)
        incidents.append(Incident(tweet))
        histo[0] += 1
        outdated_users = True

    # the only time users aren't outdated is if this tweet is thrown away or
    # if it's added to an incident without introducing a new user
    if outdated_users:
        stream.users = set.union(*[inc.users_to_track() for inc in incidents])
        print "Updating users to " + str(stream.users)
        stream.disconnect()
        stream.start()
    print histo
    # print [str(len(i.tweets)) + " " + str(len(i.users)) for i in incidents]

def track_incidents():
    incidents = []
    def rec(tweet):
        receive_tweet(incidents, tweet_to_Tweet(tweet))

    stream.set_function(rec)
    stream.keywords = set(search_terms)
    stream.start()
