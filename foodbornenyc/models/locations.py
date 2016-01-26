"""
The Location data class
"""
from datetime import datetime

from sqlalchemy import Column, Table, event
from sqlalchemy import Integer, Float, String, DateTime
# from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import mapper
from sqlalchemy import DDL

from models import metadata
from ..util.util import xstr

class Location(object):

    def __init__(self,
                 latitude=None,
                 longitude=None,
                 line1=None,
                 line2=None,
                 line3=None,
                 city=None,
                 country=None,
                 postal_code=None,
                 state=None
                 ):
        self.latitude=latitude
        self.longitude=longitude
        self.line1 = xstr(line1)
        self.line2 = xstr(line2)
        self.line3 = xstr(line3)
        self.city = xstr(city)
        self.country = xstr(country)
        self.postal_code = xstr(postal_code)
        self.state = xstr(state)
        self.street_address = self.address()

    def address(self):
        street_address = self.line1+', '+self.line2+', '+self.line3+', '+self.city+', '+self.state+' '+self.postal_code
        return street_address.lower()
    def __repr__(self):
        return "<Location (%r, %r): %s>" %\
            (self.latitude, self.longitude, self.street_address)

    def __eq__(self, other):
        if type(other) == type(self):
            if self.address() == other.address():
                return True
            else:
                return False
        else: 
            raise TypeError 

locations = Table('locations', metadata,
    #address is concat of 'line1', 'line2','line3', 'city', 'state', 'postal_code'
    Column('street_address', String(255*6), primary_key=True), # a convenience column    
    Column('latitude', Float, nullable=True),
    Column('longitude', Float, nullable=True),
    Column('line1', String(255), nullable=False, default=''),
    Column('line2', String(255), nullable=False, default=''),
    Column('line3', String(255), nullable=False, default=''),
    Column('city', String(255), nullable=False, default=''),
    Column('country', String(255), nullable=False, default=''),
    Column('postal_code', String(255), nullable=False, default=''),
    Column('state', String(255), nullable=False, default=''),
    Column('"geo_code_attempted_date"', DateTime, default=datetime.now, onupdate=datetime.now)
    )

mapper(Location, locations)

