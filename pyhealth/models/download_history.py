from datetime import date, datetime

from sqlalchemy import Column, Table
from sqlalchemy import Boolean, Date
from sqlalchemy.orm import mapper

from models import metadata


class YelpDownloadHistory(object):

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
    Column('uploaded', Boolean, nullable=False)
    )

mapper(YelpDownloadHistory, yelp_download_history)
