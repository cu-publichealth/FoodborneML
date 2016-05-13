from foodbornenyc.models.documents import Tweet
from foodbornenyc.models.users import TwitterUser
from foodbornenyc.models.locations import Location

import foodbornenyc.sources.foursquare_geo as geo

from foodbornenyc.util.util import get_logger, xuni
logger = get_logger(__name__, level="INFO")

# all possible fields from twitter that we want to import directly
user_fields = ['id_str', 'name', 'screen_name', 'location', 'description']
tweet_fields = [
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
#         'possibly_sensitive', #<type 'bool'>
        'lang', #<type 'unicode'>
        'created_at', #<type 'unicode'>
        'in_reply_to_status_id_str', #<type 'NoneType'>
#         'place', #<type 'NoneType'>
#         'metadata', #<type 'dict'>
         ]

def tweet_to_Tweet(tweet, select_fields=tweet_fields):
    """ Take tweet json and convert into a Tweet object """
    info = {k:v for (k,v) in tweet.items() if k in select_fields}
    info['text'] = xuni(tweet['text']) # convert to unicode for emoji
    info['location'] = place_to_Location(tweet['place'])
    info['user'] = user_to_TwitterUser(tweet['user'])
    return Tweet(**info)

def user_to_TwitterUser(user, select_fields=user_fields):
    """ Convert the user json from Twitter into a TwitterUser. """
    info = {k:v for (k,v) in user.items() if k in select_fields}
    return TwitterUser(**info)

location_cache = {}
def reset_location_cache():
    location_cache.clear()

def place_to_Location(place, geocode=True):
    """ Extract present fields from Twitter place and combine them into a
    Location. Saves location to temporary cache for later tweets. """
    # the documentation guarantees each place to hae an id, but experimentally
    # most/all places have full_name and bounding_box.
    if place is None: return None

    if place['id'] in location_cache:
        return location_cache[place['id']]

    l = Location()

    if 'attributes' in place and 'street_address' in place['attributes']:
        l.line1 = place['attributes']['street_address']
    if 'country' in place:
        l.country = place['country']

    if 'bounding_box' in place:
        _fill_location_bbox(l, place['bounding_box']['coordinates'][0])

        # replace all address fields with foursquare response if there is one
        if l.bbox_width == 0 and l.bbox_height == 0 and geocode:
            matches = geo.search_location(lat=l.latitude,
                                          lon=l.longitude,
                                          radius=800,
                                          query=place['full_name'])
            if matches:
                _fill_location_address(l, matches[0]['location'])

    l.id = l.identifier()
    location_cache[place['id']] = l
    return l

def _fill_location_bbox(l, box):
    l.longitude = (box[0][0]+box[2][0])/2
    l.latitude  = (box[0][1]+box[2][1])/2
    l.bbox_width = (box[2][0]-box[0][0])
    l.bbox_height  = (box[2][1]-box[0][1])

def _fill_location_address(l, address):
    l.line1 = address['address']
    l.city = address['city']
    l.country = address['country']
    l.longitude = address['lng']
    l.latitude = address['lat']

