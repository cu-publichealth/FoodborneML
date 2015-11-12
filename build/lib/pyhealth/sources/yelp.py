"""
The Yelp API model
"""

import botocore
from datetime import datetime, date, timedelta
import traceback
import requests
import time
import gzip

from ..util.util import getLogger, xstr
logger = getLogger(__name__)

config = {
    'rawdata_dir': 'pyhealth/sources/yelpfiles/', # the dir to download the yelp data from S3 to
    'local_file': 'yelp_businesses.json.gz',
    'bucket_name': 'yelp-syndication',
    'bucket_dir':  'nychealth'
    }


def downloadURLToFile(url, data_dir, filename):
    """
        Download a url to local file in streaming manner.

        This keeps a low memory footprint

        Args:
            url: the url to download from

            data_dir: the local directory to write the file

            filename: the name of the file to write

        Notes:
            You may think: That we should unzip as we download. Don't. It's really slow

        TODO: 
            * Make error handling more robust, can be misleading right now

    """
    try:
        response = requests.get(url, stream=True)

        # throw exception if response has issues
        if not response.ok:
            raise Exception

        total_size = response.headers.get('content-length')
        print "Yelp feed total size: %i MB" % (int(total_size)/(1024*1024))

        out_file = data_dir+filename
        start_time = time.time()
        with open(out_file, 'wb') as handle:

            # response ok, do the download and give info during
            block_size = 1024*4
            count = 1
            for block in response.iter_content(block_size):
                # bookkeeping display
                percent = int(count*block_size)/float(total_size)*100
                duration = time.time() - start_time
                progress_size = int(count*block_size)/(1024*1024)
                print "\r Downloading Yelp Data...%.2f%%  %i MB downloaded, %d seconds so far" %\
                        (percent, progress_size, duration),

                # write it out
                handle.write(block)
                handle.flush()
                count +=1
    except:
        logger.critical("IO error writing Yelp Data Download to local file: Check if rawdata_dir set correctly.")
        traceback.print_exc()


import botocore.session
def downloadLatestYelpData():
    """
        Attempt to download the latest gzip file from the Yelp Syndication.

        Args:
            None
        
        Returns:
            local_file: the name of where the yelp feed was downloaded to

        Note: 
            Yelp doesn't let us look at the bucket, 
            so we just try exact filenames with presigne urls for the past month
    """
    # set up botocore client
    session = botocore.session.get_session()
    client = session.create_client('s3')

    # try to donwload most recent data
    for day_delta in range(31):
        # generate the correct filenmae for a day
        dateformat = '%Y%m%d'
        day = date.today() - timedelta(day_delta)
        day_str = day.strftime(dateformat) # eg '20151008'
        ext = '_businesses.json.gz'
        filename =  day_str + ext
        logger.info("Attempting to get Yelp Reviews from %s....." % day.strftime("%m/%d/%Y"))

        # generate a presigned url for the file, since yelp doesn't give us bucket access
        url = client.generate_presigned_url('get_object',
                                           Params={'Bucket': config['bucket_name'],
                                                   'Key':config['bucket_dir'] +'/'+ filename },
                                           ExpiresIn=3600 # 1 hour in seconds
                                           )
        # do the downloading
        print "URL: ", url
        try:
            downloadURLToFile(url, config['rawdata_dir'], config['local_file'])
            break

        except Exception:
            if day_delta == 30: 
                logger.warning("NO YELP DATA AVAILABLE FOR THE PAST MONTH!")
                return
            else:
                logger.warning("no data for date: %s\n\
                     Trying the day before." % day.strftime("%m/%d/%Y"))

    logger.info("Latest Yelp Data successfully downloaded from feed.")
    local_file = config['rawdata_dir'] + config['local_file']
    return local_file

def unzipYelpFeed(filename):
    """
    Take in a .gz file and unzip it, saving it with the same file name
    """
    logger.info("Extracting file: %s" % filename)
    with gzip.open(filename, 'rb') as infile:
        rawfile = filename.strip('.gz')
        with open(rawfile, 'wb') as outfile:
            i=1
            for line in infile:
                outfile.write(line)
                if i % 1000 == 0 :
                    print "\r Extracted %i businesses so far" % i
                i += 1
    logger.info("Done extracting file: %s" % rawfile)
    return rawfile

from json import loads
from ..models.models import getDBSession
from ..models.businesses import Business, YelpCategory, businesses, categories, business_category_table
from ..models.locations import Location, locations
from ..models.documents import YelpReview, Document,yelp_reviews, documents
import sqlalchemy


#from datetime import datetime
from geopy.geocoders import Nominatim #open street map -- free :)

# @profile
def updateDBFromFeed(filename, geocode=True):
    """
    1. Take in a .gz zipped yelp review file
    2. Read in each line as a python dict through JSON, since we have one business per line
    3. Turn that dict into the approriate model objects
    4. Upsert them to DB

    """
    # database handler object
    db = getDBSession(echo=False, autoflush=False)
    # geocoder for businesses w/o lat longs
    geoLocator = Nominatim()

    logger.info("Updating Yelp DB..........")

    # setup list of businesses to skip updating
    # because we've uploaded them since yelp updated them
    # this part gets the skip condition
    newest = db.query(Business).order_by(Business.updated_at).first()
    
    if newest:
        print newest
        most_recent = newest.updated_at
        logger.info("Last updated: %r" % most_recent.strftime('%m/%d/%Y:%M:%H'))
    else:
        logger.info("First Database Population: This could take a looong time...")
        most_recent = None

    start_time = time.time()
    db_biz_ids = set([ b.id for b in db.query(Business.id).all() ])
    db_review_ids = set([ r.doc_id for r in db.query(YelpReview.doc_id).all() ])
    db_locations = set([ l.street_addres for l in db.query(Location.street_address).all() ])
    db_categories = set([ c.alias for c in db.query(YelpCategory.alias).all() ])

    if len(db_biz_ids) == 0: 
        init_db = False
    else:
        init_db = False
    # with gzip.open(filename, 'rb') as infile:
    # with gzip.open(filename, 'rb') as infile:
    with open(filename, 'rb') as infile: # for unzipped files
        biz_num = 0
        review_count = 0
        # each business is one line
        for line in infile:
            biz_num += 1
            logger.info("Updating Restaurant #%i...." % biz_num)
            current = time.time()-start_time
            m, s = divmod(current, 60)  
            h, m = divmod(m, 60)
            logger.info("Time so far: %d:%02d:%02d" % (h, m, s))
            try:
                biz = loads(line)
            except ValueError:
                logger.warning("Broken JSON Element. Skipping...")
                continue
            bdate = datetime.strptime(biz['time_updated'], '%Y-%m-%dT%H:%M:%S')#2015-10-08T20:17:50

            # skip this business if it hasn't ben updated since we last updated
            # (only works when we aren't initializing the db)
            if most_recent and not init_db:
                if bdate <= most_recent:
                    print "SKIPPING (NOT NEW): %s" % biz['name']
                    continue

            # create the Location object
            loc = dict(biz['location'])                     
            street_address = xstr(loc['address'][0])\
                +', ' +xstr(loc['address'][1])\
                +', ' +xstr(loc['address'][2])\
                + ', '+xstr(loc['city']) +', '+xstr(loc['state'])\
                + ' '+xstr(loc['postal_code'])
            
            if street_address in db_locations:
                location = db.query(Location).get(street_address)
            else:
                location = None

            # try to geocode known locations w/out latlons
            if location and not location.latitude:
                logger.info("No Lat/Long for restaurant, attempting to geocode...")
                if geocode:
                    try:
                        geo = geoLocator.geocode(street_address, timeout=2)
                        lat = geo.latitude
                        lon = geo.longitude
                    except:
                        logger.warning("Geocode failed, assigning NULL Lat/Long")
                        lat = None
                        lon = None

            # didn't find location in db so make one
            if not location:
                try: # some don't have lat,longs
                    location = Location(
                                latitude=float(loc['coordinate']['latitude']),
                                longitude=float(loc['coordinate']['longitude']),
                                line1=loc['address'][0],
                                line2=loc['address'][1],
                                line3=loc['address'][2],
                                city=loc['city'],
                                country=loc['country'],
                                postal_code=loc['postal_code'],
                                state=loc['state']
                                )
                except TypeError: # so they can't get converted to float
                    # so look them up with the geocode service
                    if geocode:
                        try:
                            logger.info("No Lat/Long for restaurant, attempting to geocode...")
                            geo = geoLocator.geocode(street_address, timeout=2)
                            lat = geo.latitude
                            lon = geo.longitude
                        except:
                            logger.warning("Geocode failed, assigning NULL Lat/Long")
                            lat = None
                            lon = None
                    else:
                        lat = None
                        lon = None
                    location = Location(
                                latitude=lat,
                                longitude=lon,
                                line1=loc['address'][0],
                                line2=loc['address'][1],
                                line3=loc['address'][2],
                                city=loc['city'],
                                country=loc['country'],
                                postal_code=loc['postal_code'],
                                state=loc['state']
                                )
                db.add(location)
                db_locations.add(street_address) # add to running list of locations

            # create the Business Object
            if biz['is_closed'] == 0: is_closed = False
            else: is_closed = True
            if biz['id'] in db_biz_ids:
                business = db.query(Business).get(biz['id'])
                business.id=biz['id']
                business.name=biz['name']
                business.phone=biz['phone']
                business.rating=biz['rating']
                business.url=biz['url']
                business.business_url=biz['business_url']
                business.last_updated=biz['time_updated']
                business.is_closed=is_closed
            else:
                business = Business(
                            id=biz['id'],
                            name=biz['name'],
                            phone=biz['phone'],
                            rating=biz['rating'],
                            url=biz['url'],
                            business_url=biz['business_url'],
                            last_updated=biz['time_updated'],
                            is_closed=is_closed
                            )
                db.add(business)

            # create all of the Reviews
            reviews = []
            for rev in biz['reviews']:
                # if the review isn't new, update it
                if rev['id'] in db_review_ids:
                    review = db.query(YelpReview).get(rev['id'])
                    review.text = rev['text']
                    review.rating=rev['rating']
                    review.user_name=rev['user']['name']
                    review.yelp_id=rev['id']
                # else create a new one
                else:
                    review = YelpReview(rating=rev['rating'],
                                        text=rev['text'],
                                        user_name=rev['user']['name'],
                                        yelp_id=rev['id'])
                    review.business_id = business.id
                    db.add(review)
                reviews.append(review)
            review_count += len(reviews)

            # create the Categories
            categories = []
            for category in biz['categories']:
                if category['alias'] in db_categories:
                    cat = db.query(YelpCategory).get(category['alias'])
                else:
                    cat =  YelpCategory(alias=category['alias'],
                                     title=category['title'])
                    db_categories.add(category['alias']) # local list
                    db.add(cat) # db 
                categories.append(cat)


            business.categories = categories
            business.reviews = reviews
            business.location = location
            db.commit()

            #if biz_num >= 50: break

    total_time = float(time.time() - start_time)
    logger.info("Upserted %i businesses and %i total reviews in %d seconds = %.2f minutes" %\
                 (biz_num, review_count, total_time,  total_time/60.))



