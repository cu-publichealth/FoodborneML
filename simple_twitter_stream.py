from twython import TwythonStreamer
from shapely.geometry import Polygon # for comparing bounding boxes efficiently
from collections import deque
import json
import os.path
import codecs
from twython import Twython, TwythonError

from datetime import datetime, timedelta
from time import sleep


def parse_twitter_timestamp(status):
    """ 
    Convert 'Wed Nov 18 15:40:46 +0000 2015' to datetime object
    Note: Python 2 can't handle the UTC offset '+0000', so slice around it
    """
    return datetime.strptime(status['created_at'][:-10] + status['created_at'][-4:], "%a %b %d %H:%M:%S %Y")

class Incident():
    """
    A data structure to keep track of local information about a pulled tweet.
    1. Keeps the the tweet filtered from the stream
    2. Gets this user's timeline going back up to 'timedelta' days
    3. Gets any conversation this tweet was involved in
    4. Tracks any future conversations this tweet is involved in
    """
    def __init__(self, status=None):
        if status is not None:
            self.start_date = parse_twitter_timestamp(status) # when the incident occured
            self.timedelta = timedelta(7) # in days, max number of days to keep from timeline
            self.conversations = [self._backtrace_conversation(status)] # all conversations involving this tweet
            self.user_timeline = self._get_user_timeline(status) # a deque of tweets by the user
            self.user = status['user']
            self.tweet0 = status['id']
        
    @classmethod
    def fromdict(cls, incident_dict):
        inc = cls(status=None)
        inc.start_date = datetime.strptime(incident_dict['start_date'], "%a %b %d %H:%M:%S %Y")
        inc.tweet0 = incident_dict['tweet0']
        inc.timedelta = timedelta(incident_dict['window'])
        inc.user = incident_dict['user']
        inc.user_timeline = incident_dict['timeline']
        inc.conversations = [ deque(convo) for convo in incident_dict['conversations'] ]
        return inc

    # public methods
    def is_over(self):
        if (self.start_date + self.timedelta) >= datetime.now():
            return True
        else:
            return False
    
    def add_if_in_this_incident(self, status):
        if self.is_over(): return False
        if status['user']['id'] == self.user['id']: # tweet involves this user
            # add to the timeline
            self.user_timeline.append(status)
            # add to any conversations if it was in one
            self._add_to_relevant_conversation(status)
            return True
        if status['in_reply_to_user_id'] == self.user['id']: # tweet was in reply to this user
            # add to any conversations if it was in one, else this reply isn't relevant
            added = self._add_to_relevant_conversation(status)
            return added
        return False
    
    def as_dict(self):
        return {
            'tweet0':self.tweet0,
            'start_date': datetime.strftime(self.start_date, "%a %b %d %H:%M:%S %Y"),
            'window': self.timedelta.days,
            'user': self.user,
            'timeline': list(self.user_timeline),
            'conversations':[ list(convo) for convo in self.conversations ]   
        }
    
    # private methods
    def _add_to_relevant_conversation(self, status):
        # note that each tweet can be in only one conversation thread, so always return on success
        reply_id = status['in_reply_to_user_id']
        if not reply_id: return False#no conversations if this wasn't a reply
        for convo in self.conversations:
            # if in reply to the end of a thread, just add it to that convo
            if reply_id == convo[-1]:
                convo.append(status)
                return True
            # now check if this response is to an earlier tweet in the convo, splitting into another convo
            for i, id in enumerate([status['id'] for status in reversed(convo)]): #traverse convo reverse chronologically
                # don't split conversations if they split before the tweet that caused the incident
                if id == self.tweet0:
                    if reply_id == id:
                        new_convo = deque(list(convo)[:len(convo)-i] + [status])
                        self.conversations.append(new_convo)
                        return True
                    else: break # got all the way back to tweet0 and reply wasn't involved, so stop analyzing this convo
                if reply_id == id:
                        new_convo = deque(list(convo)[:len(convo)-i] + [status])
                        self.conversations.append(new_convo)
                        return True
        return False
                    
    def _get_user_timeline(self, status):
        user_timeline = twitter.get_user_timeline(id=str(status['user']['id']))
        timeline = deque()
        backlimit = parse_twitter_timestamp(status) - self.timedelta
        for t in user_timeline:
            if parse_twitter_timestamp(t) >= backlimit:
                timeline.appendleft(t)
        return timeline 
        
    def _backtrace_conversation(self, status):
        convo = deque()
        convo.append(status)
        if not status['in_reply_to_status_id']: return convo # no replies to backtrace
        reply_F = True
        while reply_F:
            in_reply_to = str(status['in_reply_to_status_id'])
            try:
                status = twitter.lookup_status(id=in_reply_to)[0]
            except IndexError:
                return convo
            convo.appendleft(status) # keep conversation in chronological order
            if not status['in_reply_to_status_id']:
                reply_F = False
        return convo
    
    
from twython import TwythonStreamer
from shapely.geometry import Polygon # for comparing bounding boxes efficiently
from collections import deque
import json
import codecs

class FoodBorneStreamer(TwythonStreamer):
    """Custom streaming endpoint class. Defines how to handle incoming tweets"""
    def __init__(self, *args, **kwargs):
        TwythonStreamer.__init__(self, *args, **kwargs)
        self.output_tweets = 'stream_tweets2.json'
        self.output_incidents = 'stream_incidents2.json'
        self.counter = 0
        self.count_limit = 1000000
        self.error_counter = 0
        self.error_limit = 1000
        self.follow = deque(maxlen=5000)
        self.tweets = self.load_tweets()
        self.incidents = self.load_incidents()
        
    def on_success(self, data):
        try:
            if 'text' not in data: return
            if self.in_incident(data): #takes care of adding status to incident if True
                print "Tweet involves tracked user %r:" % (data['user'])
                print self.counter, ":: ", data['text'].encode('utf-8')
                print
                self.tweets.append(data)
                self.counter +=1
            
            elif self.in_trackterms(data) and self.in_box(data):
                print "NEW INCIDENT"
                print self.counter,':: ',data['text'].encode('utf-8')
                #print data['user'].keys()
                print
                
                self.create_incident(data)
                self.update_follow_list()
                self.tweets.append(data)
                self.save_tweet(data)
                self.counter +=1
                
            if self.counter >= self.count_limit:
                self.counter = 0
                self.save_incidents()
                self.disconnect()
        
            if self.counter % 10 == 0:
                self.save_incidents()
        except TwythonError as e:
            print "TWYTHON ERROR: SKIPPING THIS TWEET"
            print e

    
    def on_error(self, status_code, data):
            print "Error status code: ", status_code
            self.error_counter += 1
            if str(status_code) == "420": 
                print "Rate Limited: waiting a minute"
                sleep(60)
            # if self.error_counter >= self.error_limit:
            #     self.error_counter = 0
            #     self.save_incidents()
            #     self.disconnect()
                
    def run_dynamic_stream(self, filter_params):
        # initial dynamic params
        self.track = filter_params['track']
        self.location = filter_params['locations']
        
        self.statuses.set_dynamic_filter(track=','.join(self.track), 
                                         locations=','.join(self.location))
        self.statuses.dynamic_filter()
                
    def in_box(self, status):
        """recreate twitter filter to check if a tweet is in the bounding box
            1. See if coordinates in box
            2. check if place polygon intersects box
        """
        #try:
        if not self.location: 
            return True # no bounding box => anything is valid
        locationbox = [(float(self.location[0]), float(self.location[1])), (float(self.location[0]), float(self.location[3])),\
                        (float(self.location[2]), float(self.location[1])), (float(self.location[2]), float(self.location[3]))]
        if status['coordinates']:
            c = status['coordinates']
            if c['type'] == u'Point':
                coord = c['coordinates']
                if coord[0] <= self.location[0] and coord[0] >= self.location[2]\
                and coord[1] >= self.location[1] and coord[1] <= self.location[3]:
                    return True
                else:
                    return False
            elif c['type'] == u'Polygon':
                loc = Polygon([tuple(point) for point in c['coordinates']])
                box = Polygon(locationbox)
                if loc.intersects(box):
                    return True
                else:
                    return False
        elif status['place']:
            if status['place']['bounding_box']['type'] == u'Point':
                coord = status['place']['bounding_box']['coordinates']
                if coord[0] <= self.location[0] and coord[0] >= self.location[2]\
                and coord[1] >= self.location[1] and coord[1] <= self.location[3]:
                    return True
                else:
                    return False
            elif status['place']['bounding_box']['type'] == u'Polygon':
                loc = Polygon([tuple(point) for point in status['place']['bounding_box']['coordinates']][0])
                box = Polygon(locationbox)
                if loc.intersects(box):
                    return True
                else:
                    return False
        else:
            return False
        #except:
        #    print "ERROR IN_BOX"
        #    return False
        
    def in_trackterms(self, status):
        try:
            if not self.track: return True # no terms means all pass
            for term in self.track:
                if term in status['text']: return True
            return False
        except:
            return False
        
    def in_incident(self, status):
        if len(self.incidents) == 0: return False
        added = False
        for incident in self.incidents:
            added = incident.add_if_in_this_incident(status)
        return added    
    
    def update_follow_list(self):
        self.follow = deque([i.user['id'] for i in self.incidents if not i.is_over()], maxlen=5000)
        
    def create_incident(self, status):
        self.incidents.append(Incident(status=status))
        
    def save_tweet(self, status):
        with codecs.open(self.output_tweets, 'a', encoding='utf-8') as f:
            f.write(json.dumps(status)+'\n')
            
    def load_tweets(self):
        tweets = []
        if os.path.isfile(self.output_tweets):
            with codecs.open(self.output_tweets, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    tweets.append(json.loads(line))
        return tweets

    def save_incidents(self):
        with codecs.open(self.output_incidents, 'w', encoding="utf-8") as f:
            for incident in self.incidents:
                f.write(json.dumps(incident.as_dict())+'\n')

    def load_incidents(self):
        incidents = []
        if os.path.isfile(self.output_incidents):
            with codecs.open(self.output_incidents, 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    incdict = json.loads(line)
                    incidents.append(Incident.fromdict(incdict))
        return incidents
                




"""API LIMITS:
Follow: up to 5000 ids
Locations: up to 25 boxes
Terms: up to 400 terms"""
boundingbox = ['-74.259090','40.491370','-73.700272','40.915256'] # SW -> NE
trackterms=['#foodpoisoning',
            '#stomachache',
            'food poison',
            'food poisoning',
            'stomach',
            'vomit',
            'vomited',
            'puke',
            'puked',
            'diarrhea',
            'the runs',
            'got sick',
            '#theruns'
            ]
follow = []
filterparams = {'locations':boundingbox, 'track':trackterms, 'follow':follow}

if __name__ == '__main__':
    consumer_key = 'BqyVMEVyJ76DLUwwwB6sG7mc8'
    consumer_secret = '803Ztn45ruCVzUhhehOBwvhwKdmxHTOTZp1TiAYYcXRneuYUsw'
    access_token = '4211115641-bpkKfPDsiujLZYRz2OlaK9YwTHRiaL35jv7pGo3'
    access_token_secret = 'usEKY68eRfP85QkgWy69hAsF7j7xM6sq7FM3olRbdVZRO'

    twitter = Twython(consumer_key, consumer_secret, access_token, access_token_secret)

    stream = FoodBorneStreamer(consumer_key, consumer_secret, access_token, access_token_secret)
    from requests.exceptions import ChunkedEncodingError, ConnectionError
    while stream.error_counter <= stream.error_limit:
        print "ERROR COUNT: %r/%r" % ( stream.error_counter, stream.error_limit)
        try:
            stream.run_dynamic_stream(filterparams)
        # except ChunkedEncodingError as e:
        #     print e
        #     print "Resuming operations"
        #     continue
            #stream.run_dynamic_stream(filterparams)
        except Exception as e:
            stream.error_counter += 1
            print e
            sleep(5)
            print "Resuming operations"
            continue
