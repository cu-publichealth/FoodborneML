from mock import Mock, patch, call

import foodbornenyc.sources.twitter.util as util
import foodbornenyc.test.sources.twitter.sample as sample

def test_tweets_to_Tweets():
    """ Sample tweets should be converted properly """
    fields = ['text', 'id_str', 'user']
    tweets = [util.tweet_to_Tweet(sample.tweets[0], fields),
              util.tweet_to_Tweet(sample.tweets[1], fields)]
    sample.assert_matching_tweets(tweets)

def test_user_to_TwitterUser():
    # the fields should be filled in correctly
    u = util.user_to_TwitterUser(sample.user1)
    assert u.id == sample.user1['id_str']
    assert u.name == sample.user1['name']
    assert u.screen_name == sample.user1['screen_name']
    assert u.location == sample.user1['location']
    assert u.description == sample.user1['description']

@patch('foodbornenyc.sources.twitter.util.geo')
def test_place_to_Location(geo):
    # a None place should return a None location
    assert util.place_to_Location(None) == None

    # a place with no info should have nothing in the Location
    location1 = util.place_to_Location(sample.place1)
    assert location1.line1 == ''
    assert location1.country == ''

    # a large region should have its bounding box fields
    location2 = util.place_to_Location(sample.place2)
    assert location2.line1 == sample.place2['attributes']['street_address']
    assert location2.country == sample.place2['country']
    assert location2.longitude == 0
    assert location2.latitude == 0
    assert location2.bbox_width == 2
    assert location2.bbox_height == 2

    # a specific point should have its fields filled in by foursquare
    geo.search_location.return_value = sample.fsq_place
    location3 = util.place_to_Location(sample.place3)
    assert location3.bbox_width == 0
    assert location3.bbox_height == 0
    assert location3.line1 == sample.fsq_place[0]['location']['address']
    assert location3.city == sample.fsq_place[0]['location']['city']
    assert location3.country == sample.fsq_place[0]['location']['country']
    assert location3.longitude == sample.fsq_place[0]['location']['lng']
    assert location3.latitude == sample.fsq_place[0]['location']['lat']

    # requesting the same location from place should not make an extra fsq call
    location4 = util.place_to_Location(sample.place3)
    assert len(geo.search_location.call_args_list) == 1
