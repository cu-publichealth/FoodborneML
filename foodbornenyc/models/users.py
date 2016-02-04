"""
The User Model

NOTE: Not in use yet

This is currently just for twitter users
"""

from sqlalchemy import Column, Integer, Float, Unicode, UnicodeText, DateTime

class TwitterUser(object):
    __tablename__ = 'twitter_user'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255))
    screen_name = Column(Unicode(255)) # eg @handle

    #location = 

    description = Column(UnicodeText)
