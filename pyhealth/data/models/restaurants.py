"""
The restaurant model
"""

from sqlalchemy import Column, Integer, Float, String, DateTime

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base() # needed for setting up the ORM w/o explicit Tables

class Restaurant(Base):
    __tablename__ = 'location'

    id = Column(Integer, primary_key=True)

    latitude = Column(Float)
    longitude = Column(Float)

    line1 = Column(String(255))
    line2 = Column(String(255))
    line3 = Column(String(255))
    city = Column(String(255))
    country = Column(String(255))
    postal_code = Column(String(255))
    state = Column(String(255))
    updated = Column(DateTime)

    