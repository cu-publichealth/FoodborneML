"""
Database Settings
"""

try:
    from foodbornenyc.my_db_settings import database_config, twitter_config
except:
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
