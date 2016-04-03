"""
Database Settings
"""

database_config = {
    'user': 'johnnybananas',
    'password': 'placeholder_password',
    'dbhost': 'toy.db',
    'dbbackend':'sqlite'
}

twitter_config = {
    'consumer_key': '',
    'consumer_secret': '',
    'access_token': '',
    'access_token_secret': ''
}

foursquare_config = {
    'client_id': '',
    'client_secret': ''
}

try:
    from foodbornenyc.my_db_settings import *
except:
    pass
