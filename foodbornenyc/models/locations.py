"""
The Location data class
"""
from datetime import datetime

from sqlalchemy import Column, Table
from sqlalchemy import Float, String, DateTime
from sqlalchemy.orm import mapper

from foodbornenyc.models.metadata import metadata
from foodbornenyc.util.util import xstr

class Location(object):
    """Location data model.

    For saving locations of `Business`es, `Tweet`s, `TwitterUser`s, etc.
    """
    def __init__(self,
                 latitude=None,
                 longitude=None,
                 line1=None,
                 line2=None,
                 line3=None,
                 city=None,
                 country=None,
                 postal_code=None,
                 state=None):
    
        self.latitude = latitude
        self.longitude = longitude
        self.line1 = xstr(line1)
        self.line2 = xstr(line2)
        self.line3 = xstr(line3)
        self.city = xstr(city)
        self.country = xstr(country)
        self.postal_code = xstr(postal_code)
        self.state = xstr(state)
        self.street_address = self.address()

        # TODO: Add bounding boxes of places where the lat/lon then becomes the center

    def address(self):
        """Convert all of the normal address fields into one canonical `street_address`"""
        street_address = (self.line1 + ', ' + self.line2 + ', ' + self.line3
                          + ', ' + self.city + ', ' + self.state + ' ' + self.postal_code)
        return street_address.lower()

    def __repr__(self):
        return "<Location (%r, %r): %s>" % (self.latitude, self.longitude, self.street_address)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.address() == other.address()
        else:
            raise TypeError

locations = Table('locations', metadata,
                  # address is concat of 'line1', 'line2','line3', 'city', 'state', 'postal_code'
                  # ultimately it's a convienience column
                  Column('street_address', String(255*6), primary_key=True),
                  Column('latitude', Float, nullable=True),
                  Column('longitude', Float, nullable=True),
                  Column('line1', String(255), nullable=False, default=''),
                  Column('line2', String(255), nullable=False, default=''),
                  Column('line3', String(255), nullable=False, default=''),
                  Column('city', String(255), nullable=False, default=''),
                  Column('country', String(255), nullable=False, default=''),
                  Column('postal_code', String(255), nullable=False, default=''),
                  Column('state', String(255), nullable=False, default=''),
                  Column('geo_code_attempted_date', DateTime,
                         default=datetime.now, onupdate=datetime.now))

mapper(Location, locations)

