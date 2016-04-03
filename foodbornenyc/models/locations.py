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
                 bbox_width=None,
                 bbox_height=None,
                 line1=None,
                 line2=None,
                 line3=None,
                 city=None,
                 country=None,
                 postal_code=None,
                 state=None,
                 place_id=None):
        #self.latitude = latitude
        #self.longitude = longitude
        self.line1 = xstr(line1)
        self.line2 = xstr(line2)
        self.line3 = xstr(line3)
        self.city = xstr(city)
        self.country = xstr(country)
        self.postal_code = xstr(postal_code)
        self.state = xstr(state)
        #self.bbox_width = bbox_width
        #self.bbox_height = bbox_height

        # primary key for addresses: either the Twitter place id or a concat of
        # the other fields for yelp businesses. a decent preliminary identifier
        self.street_address = place_id or self.address()

    def bbox(self):
        return {'left': self.longitude - self.bbox_width/2,
                'right': self.longitude + self.bbox_width/2,
                'top': self.latitude - self.bbox_height/2,
                'bottom': self.latitude + self.bbox_height/2 }

    def address(self):
        """Convert all the normal addr fields to 1 canonical `street_address`"""
        # street address lines if available
        street_address = (self.line1 + ', ' + self.line2 + ', ' + self.line3
                          + ', ' + self.city + ', ' + self.state + ' '
                          + self.postal_code)
        return street_address.lower()

    def __repr__(self):
        return "<Location (%r, %r): %s>" % (self.latitude, self.longitude,
                    self.street_address)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.address() == other.address()
        else:
            raise TypeError

locations = Table('locations', metadata,
                  Column('street_address', String(255*6), primary_key=True),
                  # Column('latitude', Float, nullable=True),
                  # Column('longitude', Float, nullable=True),
                  # Column('bbox_width', Float, nullable=True),
                  # Column('bbox_height', Float, nullable=True),
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

