"""
Yelp Deployment

This file defines the functions that are called daily why deploying the system
"""
import schedule
import time

from ..sources import yelp_fast as Yelp
def download():
    """ download syndication from Yelp and upsert to database"""
    fname = Yelp.downloadLatestYelpData()
    data = Yelp.unzipYelpFeed(fname)
    Yelp.updateDBFromFeed(data, geocode=False)

from ..settings import geocode_wait_time
def geocode():
    """ try to geocode unknown locations """
    Yelp.geocodeUnknownLocations(wait_time=geocode_wait_time)


def deploy():
    # define workload schedule
    schedule.every().day.at("8:0").do(download) # download at 8AM
    schedule.every().day.at("23:00").do(geocode) # Geocode at 11PM

    # run the continuous program
    while True:
        schedule.run_pending()
        time.sleep(1) # wait one second