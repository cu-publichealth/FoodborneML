"""
The document model class, and its subclasses:

1. YelpReview
2. Tweet

"""

from ...util.util import getLogger

from locations import Location
from businesses import Business

from sqlalchemy import Column, Integer, String, UnicodeText, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

from base import Base

class Document(Base):
    __tablename__ = 'document'

    id = Column(Integer, primary_key=True)
    text = Column(UnicodeText)
    type = Column(String(50))
    created_date = Column(DateTime)

    __mapper_args__ = {
        'polymorphic_identity':'document',
        'polymorphic_on':type
    }

class YelpReview(Document):
    __tablename__ = 'yelp_review'

    id = Column(Integer, ForeignKey('document.id'), primary_key=True)
    
    business_id = Column(Integer, ForeignKey(Business.id))
    business = relationship(Business, backref=backref('yelp_review'))

  

    __mapper_args__ = {
        'polymorphic_identity':'yelp_review',
    }

class Tweet(Document):
    __tablename__ = 'tweet'

    id = Column(Integer, ForeignKey('document.id'), primary_key=True)
    
    location_id = Column(Integer, ForeignKey(Location.id))
    location = relationship(Location, backref=backref('tweet'))
    
    __mapper_args__ = {
        'polymorphic_identity':'tweet',
    }
