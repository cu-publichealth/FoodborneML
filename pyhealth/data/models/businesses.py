"""
The Yelp models

1. Business
2. YelpCategory

"""

from locations import Location

from sqlalchemy import Column, Integer, Float, String, Unicode, DateTime
from sqlalchemy import Table, ForeignKey
from sqlalchemy.orm import relationship, backref

from base import Base

business_category_table = Table('business_category', Base.metadata,
        Column('business_id', Integer, ForeignKey('business.id')),
        Column('category_id', Integer, ForeignKey('yelp_category.id')))

class Business(Base):
    __tablename__ = 'business'

    id = Column(Integer, primary_key=True)

    name = Column(Unicode(191))
    phone = Column(String(20))
    rating = Column(Float)
    url = Column(String(255))
    business_url = Column(String(255))

    location_id = Column(Integer, ForeignKey(Location.id))
    location = relationship(Location, backref=backref('business'))

    categories =  relationship("YelpCategory", 
            secondary=business_category_table)

    updated = Column(DateTime)

class YelpCategory(Base):
    __tablename__ = 'yelp_category'

    id = Column(Integer, primary_key=True)

    alias = Column(String(255))
    title = Column(String(255))

    businesses =  relationship("Business", 
        secondary=business_category_table)

