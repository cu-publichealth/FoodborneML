"""
YelpDownloadHistory for bookkeeping the daily yelp feed downloads.

If we've downloaded, unzipped, and uploaded today, no sense in repeating ourselves
"""

from datetime import date, datetime

from sqlalchemy import Column, Table
from sqlalchemy import Boolean, Date
from sqlalchemy.orm import mapper

from foodbornenyc.models.metadata import metadata

class YelpDownloadHistory(object):
    """Bookkeeping data model for downloading the daily yelp syndication

    Each day the zipped file is downloaded, unzipped, and uploaded to the DB.

    This table keeps track of whether or not each of those stages has happened today.
    """
    def __init__(self):
        self.date = date.today()
        self.downloaded = False
        self.unzipped = False
        self.uploaded = False

    def __repr__(self):
        return ("<YelpDownloadHistory: %s, Down:%r, Up:%r>"
                % (datetime.strftime(self.date, "%m/%d/%Y"),
                   self.downloaded,
                   self.uploaded))

yelp_download_history = Table('yelp_download_history', metadata,
                              Column('date', Date, primary_key=True),
                              Column('downloaded', Boolean, nullable=False),
                              Column('unzipped', Boolean, nullable=False),
                              Column('uploaded', Boolean, nullable=False))

mapper(YelpDownloadHistory, yelp_download_history)
