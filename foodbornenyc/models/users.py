"""
The User Model

This is currently just for twitter users
"""
from sqlalchemy import Column, Table
from sqlalchemy import Integer, Unicode, UnicodeText, DateTime, String
from sqlalchemy.orm import mapper, relationship, backref

from foodbornenyc.models.metadata import metadata


class TwitterUser(object):
    def __init__(self,
                 id_str,
                 name=None,
                 screen_name=None,
                 location=None,
                 description=None):
        self.id = str(id_str)
        self.name = name
        self.screen_name = screen_name # e.g. @handle
        self.location = location
        self.description = description

    def __repr__(self):
        return "<TwitterUser(%s: %s)>" % (self.id, self.screen_name)

twitter_users = Table('twitter_users', metadata,
                      Column('id', String(64), primary_key=True),
                      Column('name', Unicode(255)),
                      Column('screen_name', Unicode(255)),
                      Column('location', Unicode(255), nullable=True),
                      Column('description', UnicodeText, nullable=True))

mapper(TwitterUser, twitter_users)
#mapper(TwitterUser, twitter_users,
#       properties={
#           'tweets': relationship('Tweet', backref=backref('twitter_user'))
#       })
