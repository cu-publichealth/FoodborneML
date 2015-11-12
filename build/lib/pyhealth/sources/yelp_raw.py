"""
The Yelp API model
"""

import botocore
import datetime
import traceback
import requests
import time
import gzip

from ..util.util import getLogger
logger = getLogger(__name__)

config = {
    'rawdata_dir': 'pyhealth/data/sources/yelpfiles/', # the dir to download the yelp data from S3 to
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
        day = datetime.date.today() - datetime.timedelta(day_delta)
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
        with open(filename.strip('.gz'), 'wb') as outfile:
            outfile.write('[') # make it an array of objects
            i=1
            for line in infile:
                if i==1:
                        outfile.write(line.replace('{"business_url"', '{"business_url"')+'\n')
                else:
                    outfile.write(line.replace('{"business_url"', ',{"business_url"')+'\n')
                i += 1
            outfile.write("]")
    logger.info("Done extracting file: %s" % filename)

from json import loads
from ..models.models import getDBSession
from ..models.businesses import Business, YelpCategory
from ..models.locations import Location
from ..models.documents import YelpReview
from datetime import datetime
from geopy.geocoders import Nominatim

def updateDBFromYelpFeed(filename):
    """
    1. Take in a .gz zipped yelp review file
    2. Read in each line as a python dict through JSON, since we have one business per line
    3. Turn that dict into the approriate model objects
    4. Upsert them to DB

    """
    # database handler object
    db = getDBSession()#echo=True)

    # geocoder for businesses w/o lat longs
    geoLocator = Nominatim()

    logger.info("Extracting file: %s" % filename)
    logger.info("Updating Yelp DB..........")

    # setup first set of batch lists
    # insert lists
    # i_batch_categories = []
    # i_batch_locations = []
    # i_batch_businesses = []
    # i_batch_reviews = []
    # # update lists
    # u_batch_categories = []
    # u_batch_locations = []
    # u_batch_businesses = []
    # u_batch_reviews = []

    # setup list of businesses to skip updating
    # because we've uploaded them since yelp updated them
    # this part gets the skip condition
    newest = db.query(Business).order_by(Business.updated_at).first()

    # these are to pick insert or update instead of merge, which is slow
    # get the set of urls for businesses already in db
    #db_businesses = set([url for in db.query(Business.url).all()])
    # get the set of uniquely identifying location strings for all locations in db
    #db_locations = set([ l.line1+l.line2+l.line3+l.city+l.state+l.postal_code \
    #                    for l in db.query(Location.line1, Location.line2, Location.line3, Location.city, Location.state, Location.postal_code)\
    #                    .all() ])
    # get the set of all yelp review id string in the database
    #db_review_ids = set([ yelp_id for yelp_id in db.query(YelpReview.yelp_id).all()])
    # get the set of all category aliases in db
    #db_categories = set([ alias for alias in db.query(YelpCategory.alias).all() ])
    
    if newest:
        print newest
        most_recent = newest.updated_at
        logger.info("Last updated: ", most_recent.stftime('%m/%d/%Y:%M:%H'))
    else:
        logger.info("First Database Population: This could take a looong time...")
        most_recent = None

    start_time = time.time()
    # with gzip.open(filename, 'rb') as infile:
    with open(filename, 'rb') as infile: # for unzipped files
        biz_num = 0
        review_count = 0
        # each business is one line
        for line in infile:
            biz_num += 1
            upload_modulo = 50
            logger.info("Updating Restaurant #%i...." % biz_num)
            biz = loads(line)
            # skip this business if it hasn't ben updated since we last updated
            if biz['time_updated'] <= most_recent:
                print "SKIPPING (NOT NEW): %s" % biz['name']
                continue


            loc = dict(biz['location'])

            # preprocessing to make sure we don't do way too much work
            # setup lists of elements to merge in batches
            if biz_num % upload_modulo == 0:
                batch_categories = []
                batch_locations = []
                batch_businesses = []
                batch_reviews = []


            # create the Categories
            categories = []
            for category in biz['categories']:
                categories.append(
                    YelpCategory(alias=category['alias'],
                                 title=category['title'])
                    )
            batch_categories.extend(categories)
            # create the Location object
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
                            state=loc['state'],
                            updated_at=None
                            )
            except TypeError: # so they can't get converted to float
                # so look them up with the geocode service
                logger.info("No Lat/Long for restaurant, attempting to geocode...")
                street_address = ' '.join(loc['address'])\
                                + ', '+ loc['city'] +', '+loc['state']\
                                + ', '+loc['country']+ ' '+loc['postal_code']
                try:
                    geo = geoLocator.geocode(street_address, timeout=5)
                    lat = geo.latitude
                    lon = geo.longitude
                except:
                    logger.warning("Geocode failed, assigning NULL Lat/Long")
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
                            state=loc['state'],
                            updated_at=None
                            )
            batch_locations.append(location)

            # create the Business Object
            if biz['is_closed'] == 0: is_closed = False
            else: is_closed = True
            business = Business(
                        name=biz['name'],
                        phone=biz['phone'],
                        rating=biz['rating'],
                        url=biz['url'],
                        business_url=biz['business_url'],
                        last_updated=biz['time_updated'],
                        updated_at=None,
                        is_closed=is_closed
                        )
            batch_businesses.append(business)

            # create all of the reviews
            reviews = []
            for rev in biz['reviews']:
                review = YelpReview(rating=rev['rating'],
                                   text=rev['text'],
                                   user_name=rev['user']['name'])
                review.business_id = business.id
                reviews.append(review)

            review_count += len(reviews)
            batch_reviews.extend(reviews)

            # set relations
            business.categories = categories
            business.reviews = reviews
            business.location = location

            # merge them all to the DB if a merge iteration
            if biz_num % upload_modulo == 0:
                start = time.time()
                logger.info("Upserting batch #%i....(May Take a while)" % (biz_num/upload_modulo))
                for category in batch_categories: db.merge(category)
                for location in batch_locations: db.merge(location)
                for business in batch_businesses: db.merge(business)
                for review in batch_reviews: db.merge(review)
                db.commit()
                logger.info("Uploaded batch in %d seconds" % (time.time()- start))

            #for category in categories: db.merge(category)
            #raw_input("Merged Categories... continue? [enter]")
            #db.merge(location)
            #raw_input("Merged Location... continue? [enter]")
            #db.merge(business)
            #raw_input("Merged Business... continue? [enter]")
            #for review in reviews: db.merge(review)
            #raw_input("Merged Reviews... continue? [enter]")

    # once we're done, merge what's left
    start = time.time()
    logger.info("Upserting last batch....")
    for category in batch_categories: db.merge(category)
    for location in batch_locations: db.merge(location)
    for business in batch_businesses: db.merge(business)
    for review in batch_reviews: db.merge(review)
    db.commit()
    logger.info("Uploaded batch in %d seconds" % (time.time()- start))


    total_time = float(time.time() - start_time)
    logger.info("Upserted %i businesses and %i total reviews in %d seconds = %.2f minutes" %\
                 (biz_num, review_count, total_time,  total_time/60.))



