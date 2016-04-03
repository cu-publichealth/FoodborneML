"""
The Location data class
"""
from datetime import datetime

from sqlalchemy import Column, Table, CheckConstraint
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
                 state=None):
        self.latitude = latitude
        self.longitude = longitude
        self.bbox_width = bbox_width
        self.bbox_height = bbox_height

        self.line1 = xstr(line1)
        self.line2 = xstr(line2)
        self.line3 = xstr(line3)
        self.city = xstr(city)
        self.country = xstr(country)
        self.postal_code = xstr(postal_code)
        self.state = xstr(state)

        self.id = self.identifier()

    def bbox(self):
        return {'left': self.longitude - self.bbox_width/2,
                'right': self.longitude + self.bbox_width/2,
                'top': self.latitude - self.bbox_height/2,
                'bottom': self.latitude + self.bbox_height/2 }

    def identifier(self):
        """ Makes an identifier string for the object for convenience """
        return location_id(self.__dict__)

    def __repr__(self):
        return "<Location (%r, %r): %s>" % (self.latitude, self.longitude,
                    self.id)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.identifier() == other.identifier()
        else:
            raise TypeError

def location_id(location_dict):
    """ Takes a dictionary of location information to make an identifer string.
    This is defined outside the Location object as a faster avenue. """
    d = location_dict
    iden = "%s|%s|%s|%s|%s|%s" % \
            (d['line1'], d['line2'], d['line3'], d['city'], d['state'],
             d['postal_code'])
    if d['bbox_width'] and d['bbox_height']:
        iden += "|%r|%r" % (d['bbox_width'], d['bbox_height'])

    return iden.lower()


locations = Table('locations', metadata,
    Column('id', String(255*6), nullable=False, primary_key=True),

    Column('latitude', Float, nullable=True),
    Column('longitude', Float, nullable=True),
    Column('bbox_width', Float, nullable=True),
    Column('bbox_height', Float, nullable=True),

    CheckConstraint('(bbox_width IS NOT NULL AND bbox_height IS NOT NULL AND '
                    'latitude IS NOT NULL AND longitude IS NOT NULL) OR'
                    '(bbox_width IS NULL AND bbox_height IS NULL AND '
                    'latitude IS NULL AND longitude IS NULL)',
                    name='valid_bbox'),

    Column('line1', String(255), nullable=False, default=''),
    Column('line2', String(255), nullable=False, default=''),
    Column('line3', String(255), nullable=False, default=''),
    Column('city', String(255), nullable=False, default=''),
    Column('country',String(255),nullable=False,default=''),
    Column('postal_code', String(255), nullable=False, default=''),
    Column('state', String(255), nullable=False, default=''),

    Column('geo_code_attempted_date', DateTime,
         default=datetime.now, onupdate=datetime.now)
)

mapper(Location, locations)

