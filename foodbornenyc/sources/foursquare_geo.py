from foursquare import Foursquare
from foodbornenyc.db_settings import foursquare_config

fsq = Foursquare(**foursquare_config)

# rate limits: 5000 per hour, 1.388... a second for venue endpoints
# foursquare's API is really versatile in being able to fill in missing fields

def search_location(lat=None, lon=None, query='', radius=None):
    intent = 'browse' if radius is not None else 'checkin'
    params = {'intent':intent, 'query':query}
    if ((lat and lon) is not None):
        params['ll'] = '%s,%s' % (lat,lon)
    if (radius is not None):
        params['radius'] = radius

    return fsq.venues.search(params=params)['venues']

