"""
The Yelp models

1. Business
2. YelpCategory

"""
from datetime import datetime

from sqlalchemy import Column, Table, ForeignKey, ForeignKeyConstraint, PrimaryKeyConstraint, event
from sqlalchemy import Integer, Float, String, Unicode, Boolean, DateTime
from sqlalchemy.orm import mapper, relationship, backref
from sqlalchemy import DDL

from models import metadata

from locations import Location
from documents import YelpReview

business_category_table = Table('businesses_categories', metadata,
        Column('business_id', String(64)), 
        Column('category_alias', String(255)),         
        ForeignKeyConstraint( ['business_id'], ['businesses.id'], name='fk_biz_id'),
        ForeignKeyConstraint( ['category_alias'], ['yelp_categories.alias'], name='fk_cat_alias'),
        PrimaryKeyConstraint('business_id', 'category_alias')
         )

class YelpCategory(object):

    def __init__(self, alias=None, title=None):
        self.alias = alias
        self.title = title

    def __repr__(self):
        return '<YelpCategory title%r:alias%r>' % (self.title, self.alias)

categories = Table('yelp_categories', metadata,
    Column('alias', String(255), primary_key=True),
    Column('title', String(255))
    )

mapper(YelpCategory, categories)

class Business(object):

    def __init__(self, 
                id=None,
                name=None,
                phone=None,
                rating=None,
                url=None,
                business_url=None,
                last_updated=None,
                is_closed=False):
        self.id = id
        self.name = name
        self.phone = phone
        self.rating= rating
        self.url = url
        self.business_url = business_url
        self.last_updated = last_updated # last time Yelp updated the item
        self.is_closed = is_closed

    def __repr__(self):
        return '<Business name%r>' % ( self.name)

businesses = Table('businesses', metadata,
    Column('id', String(64), primary_key=True),
    Column('url', String(255)),
    Column('name', Unicode(191)),
    Column('phone', String(20), nullable=True),
    Column('rating', Float),
    Column('business_url', String(255), nullable=True),
    Column('last_updated', DateTime),
    Column('updated_at', DateTime, default=datetime.now, onupdate=datetime.now),
    Column('is_closed', Boolean, nullable=False, default=False),
    Column('location_address', String(255*6)), 
    ForeignKeyConstraint( ['location_address'], ['locations.street_address'], name='fk_loc')
    )

mapper(Business, businesses, properties={
    'location': relationship(Location, backref=backref('businesses')),
    'reviews': relationship(YelpReview, backref=backref('businesses')),
    'categories': relationship(YelpCategory, secondary=business_category_table, backref="businesses")
    })
