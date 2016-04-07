# sample places, users, and tweets for testing

place1 = {'id': '12345'}
place2 = {'id': '23456',
          'attributes': {'street_address': '1234 Broadway'},
          'country': 'United States',
          "bounding_box": { "coordinates": [[
              [-1, -1],
              [1, -1],
              [1, 1],
              [-1, 1]]],
              "type": "Polygon"},
          }
place3 = {'id': '34567',
          'full_name': 'The Place',
          'country': 'United States',
          'bounding_box': { 'coordinates': [[
              [1, 1],
              [1, 1],
              [1, 1],
              [1, 1]]],
              'type': 'Polygon'},
          }
fsq_place = [{'location': {
            'address': '11 Broadway',
            'city': 'New York',
            'country': 'United States',
            'lat': '1.1',
            'lng': '0.9'
            }}]
user1 = {'id_str': '3333',
        'name': 'Bobby',
        'screen_name': 'bob',
        'location': 'The Internet',
        'description': 'Bobbin\''
        }
user2 = {'id_str': '444',
        'name': 'Jimmy',
        'screen_name': 'jim',
        'location': 'The Outernet',
        'description': 'Jammin\''
        }

tweets = [ {
            'id_str':'2',
            'text':"I hate food!",
            'user': user1,
            'in_reply_to_user_id_str': None,
            'lang': 'en',
            'created_at': 'Tue Feb 23 23:40:54 +0000 2015',
            'in_reply_to_status_id_str': None,
            'place': place2
        }, {
            'id_str':'34',
            'text':"My stomach hurts!",
            'user': user1,
            'in_reply_to_user_id_str': None,
            'lang': 'en',
            'created_at': 'Tue Feb 23 21:00:11 +0000 2015',
            'in_reply_to_status_id_str': None,
            'place': place2
        }]

def assert_matching_tweets(t):
    """ Helper method for checking if tweets match sample """
    assert len(t) == 2
    assert t[0].text == tweets[0]['text']
    assert t[0].id == tweets[0]['id_str']
    assert t[1].text == tweets[1]['text']
    assert t[1].id == tweets[1]['id_str']
    assert t[1].location.line1 == place2['attributes']['street_address']
