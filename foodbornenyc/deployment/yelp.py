"""
Yelp Deployment

This file defines the functions that are called daily why deploying the system
"""
import schedule
import time

from ..sources import yelp_fast as Yelp
def download():
    """ download syndication from Yelp and upsert to database"""
    fname = Yelp.download_latest_yelp_data()
    data = Yelp.unzip_file(fname)
    Yelp.upsert_yelpfile_to_db(data, geocode=False)

from ..methods import yelp_classify
from..settings import yelp_classify_config
def classify():
    clf = yelp_classify.YelpClassify()
    clf.classify_reviews(since=yelp_classify_config['days_back'],
                         verbose=yelp_classify_config['verbosity'])

from ..settings import geocode_config
def geocode():
    """ try to geocode unknown locations """
    Yelp.geocodeUnknownLocations(wait_time=geocode_config['wait_time'],
                                 runt_time=geocode_config['run_time'])


def deploy():
    # define workload schedule
    schedule.every().day.at("8:00").do(download) # download at 8AM
    schedule.every().day.at("8:30").do(classify) # classify new at 9AM
    schedule.every().day.at("23:00").do(geocode) # Geocode at 11PM

    # run the continuous program
    while True:
        schedule.run_pending()
        time.sleep(1) # wait one second
