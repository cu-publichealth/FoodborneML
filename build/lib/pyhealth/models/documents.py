"""
The document model class, and its subclasses:

1. YelpReview
2. Tweet

"""
from datetime import datetime

from sqlalchemy import Column, Table, event
from sqlalchemy import Integer, Float, String, UnicodeText, DateTime
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship, backref, relation, class_mapper

from models import metadata

class YelpReview(object):

    def __init__(self, rating=None, text=None, user_name=None, yelp_id=None):
        self.rating=rating
        self.text = text
        self.user_name = user_name
        self.yelp_id = yelp_id

    def __repr__(self):
        return "<YelpReview: %r>" % self.text

yelp_reviews = Table('yelp_reviews', metadata,
    Column('yelp_id', String(64), primary_key=True),
    Column('text', UnicodeText),
    Column('rating', Float),
    Column('user_name', String(255)),    
    Column('created', DateTime),
    Column('updated_at', DateTime, default=datetime.now, onupdate=datetime.now),
    Column('business_id', String(64), nullable=False),
    ForeignKeyConstraint( ['business_id'], ['businesses.id'], name='fk_rev_biz_id'),
    )
mapper(YelpReview, yelp_reviews)

class Document(object):
    def __init__(self, name):
        self.type = name

"""
NOTE: There is currently an issue with the document class:
    Because it lacks any KeyConstraints on the associated tables,
    If you delete subtype of a document without deleting the corresponding doc,
    You will leave hanging references... Not good

TODO: Fix this!

"""

documents = Table("documents", metadata,
    Column('id', String(64), primary_key=True),
    Column('type', String(50), nullable=False)
)
mapper(Document, documents)

