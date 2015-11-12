"""
Download the Yelp feed and update the DB

    *** CURRENTLY DEPRECATED ***

    This just calls a jar file fromthe old system that's heavily optimized 
    to upsert thousands of yelp businesses every day to the DB
"""
from datetime import datetime

from sqlalchemy import Column, Table, event
from sqlalchemy import Integer, Float, String, DateTime
from sqlalchemy.dialects.mssql import DATETIME2
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
    # allows NULL lat/longs with different street addresses,postal codes
    #UniqueConstraint('line1', 'line2','line3',\
    #    'city', 'state', 'postal_code') 
    )

mapper(Location, locations)

# an upsert trigger to make sqlalchemy add_all waaaay faster
# http://database-programmer.blogspot.com/2009/06/approaches-to-upsert.html
#locations_trigger = DDL(
    # """
    # CREATE TRIGGER upsert_locations
    # ON locations
    # INSTEAD OF insert
    # AS
    # BEGIN
    #     SET NOCOUNT ON;
    #     DECLARE @result       int;
    #     DECLARE @new_street_address VARCHAR(1530); 
    #     DECLARE @new_latitude FLOAT; 
    #     DECLARE @new_longitude FLOAT; 
    #     DECLARE @new_line1 VARCHAR(255);
    #     DECLARE @new_line2 VARCHAR(255);
    #     DECLARE @new_line3 VARCHAR(255);
    #     DECLARE @new_city VARCHAR(255);
    #     DECLARE @new_country VARCHAR(255);
    #     DECLARE @new_postal_code VARCHAR(255);
    #     DECLARE @new_state VARCHAR(255);
    #     DECLARE @new_geo_code_attempted_date DATETIME;

    #     DECLARE trig_ins_locations CURSOR FOR 
    #             SELECT * FROM inserted;
    #     OPEN trig_ins_locations;

    #     FETCH FROM trig_ins_locations
    #      INTO @new_street_address, 
    #              @new_latitude,
    #              @new_longitude, 
    #              @new_line1,
    #              @new_line2,
    #              @new_line3,
    #              @new_city,
    #              @new_country,
    #              @new_postal_code,
    #              @new_state,
    #              @new_geo_code_attempted_date;

    #     WHILE @@Fetch_status = 0 
    #     BEGIN
    #         -- Find out if there is a row now
    #         SET @result = (SELECT count(*) from locations
    #                         WHERE street_address = @new_street_address
    #                       )
        
    #         IF @result = 1 
    #         BEGIN
    #             -- Since there is already a row, do an
    #             -- update
    #             UPDATE locations
    #                SET  latitude = @new_latitude,
    #                      longitude = @new_longitude, 
    #                      line1 = @new_line1,
    #                      line2 = @new_line2,
    #                      line3 = @new_line3,
    #                      city = @new_city,
    #                      county = @new_country,
    #                      postal_code= @new_postal_code,
    #                      state = @new_state,
    #                      geo_code_attempted_date = @new_geo_code_attempted_date
    #              WHERE street_address = @new_street_address;
    #         END
    #         ELSE
    #         BEGIN
    #             -- When there is no row, we insert it
    #             INSERT INTO locations
    #                 ( street_address, 
    #                      latitude,
    #                      longitude, 
    #                      line1,
    #                      line2,
    #                      line3,
    #                      city,
    #                      country,
    #                      postal_code,
    #                      state,
    #                      geo_code_attempted_date)
    #             VALUES
    #                   ( @new_street_address, 
    #                      @new_latitude,
    #                      @new_longitude, 
    #                      @new_line1,
    #                      @new_line2,
    #                      @new_line3,
    #                      @new_city,
    #                      @new_country,
    #                      @new_postal_code,
    #                      @new_state,
    #                      @new_geo_code_attempted_date)
    #             UPDATE locations

    #         -- Pull the next row
    #         FETCH NEXT FROM trig_ins_locations
    #          INTO @new_street_address, 
    #              @new_latitude,
    #              @new_longitude, 
    #              @new_line1,
    #              @new_line2,
    #              @new_line3,
    #              @new_city,
    #              @new_country,
    #              @new_postal_code,
    #              @new_state,
    #              @new_geo_code_attempted_date;

    #     END  -- Cursor iteration

    #     CLOSE trig_ins_locations;
    #     DEALLOCATE trig_ins_locations;

    # END
    # """
#)

# event.listen(
#     locations,
#     'after_create',
#     locations_trigger.execute_if(dialect='mssql')
# )
