"""
The Yelp API model
"""

import botocore.session
from datetime import datetime, date, timedelta
import traceback
import requests
import time
import gzip
from json import loads

from sqlalchemy import exists, desc
from geopy.geocoders import Nominatim #open street map -- free :)

# import sqlalchemy
from foodbornenyc.models.models import get_db_session
from foodbornenyc.models.download_history import YelpDownloadHistory
from foodbornenyc.models.businesses import Business, YelpCategory
from foodbornenyc.models.businesses import businesses, categories, business_category_table
from foodbornenyc.models.locations import Location, locations
from foodbornenyc.models.documents import YelpReview, Document
from foodbornenyc.models.documents import yelp_reviews, documents, document_associations

from foodbornenyc.settings import yelp_download_config as config
from foodbornenyc.db_settings import database_config as dbconfig

from foodbornenyc.util.util import get_logger, xstr, xuni, sec_to_hms
logger = get_logger(__name__)

def download_url_to_file(url, data_dir, filename):
    """Download a url to local file.

        Write to file as stream. This keeps a low memory footprint

        Args:
            url (str): the url to download from

            data_dir (str): the local directory to write the file

            filename (str): the name of the file to write

        Returns:
            None
            
    """
    response = requests.get(url, stream=True)

    # throw exception if response has issues
    if not response.ok:
        # TODO: This is poor handling, make it more explicit
        logger.warning("BAD RESPONSE")
        raise Exception

    total_size = response.headers.get('content-length')
    logger.info("Yelp feed total size: %i MB", int(total_size)/(1024*1024))

    out_file = data_dir + filename
    start_time = time.time()
    # you may think: we should unzip as we download. Don't. It's really slow
    with open(out_file, 'wb') as handle:
        # response ok, do the download and give info during
        block_size = 1024*4
        count = 1
        for block in response.iter_content(block_size):
            # bookkeeping display
            percent = int(count*block_size)/float(total_size)*100
            duration = time.time() - start_time
            progress_size = int(count*block_size)/(1024*1024)
            if count % 100 == 0:
                # the only place not logging is ok: when doing carriage returns (logging can't)
                print "\r Downloading Yelp Data...%.2f%%  %i MB downloaded, %d seconds so far" %\
                      (percent, progress_size, duration),

            # write it out
            handle.write(block)
            handle.flush()
            count +=1
    print # gets rid of final carriage return
    
def download_latest_yelp_data():
    """Attempt to download the latest gzip file from the Yelp Syndication.

        Args:
            None
        
        Returns:
            local_file: the name of where the yelp feed was downloaded to

        Notes: 
            Yelp doesn't let us look at the bucket, 
            so we just try exact filenames with presigned urls for the past month
    """
    #get whhere to save the feed from config
    local_file = config['rawdata_dir'] + config['local_file']

    # first make sure we haven't already downloaded the file
    db = get_db_session()
    ydh = db.query(YelpDownloadHistory).filter(YelpDownloadHistory.date==date.today()).scalar()

    # if it doesn't exist or it's old, create the new one
    if not ydh or not ydh.date == date.today():
        ydh = YelpDownloadHistory()
        db.add(ydh)
        db.commit()
        logger.info("Creating new download history for today")

    # if we already downloaded, log and return
    if ydh.downloaded:
        logger.info("Already downloaded the Yelp feed for today...")
        return local_file

    # set up botocore client
    session = botocore.session.get_session()
    client = session.create_client('s3')

    # try to download most recent data (go up to one month back)
    for day_delta in range(31):
        # generate the correct filename for a day
        dateformat = '%Y%m%d'
        day = date.today() - timedelta(day_delta)
        day_str = day.strftime(dateformat) # eg '20151008'
        ext = '_businesses.json.gz'
        filename =  day_str + ext
        logger.info("Attempting to get Yelp Reviews from %s.....", day.strftime("%m/%d/%Y"))

        # generate a presigned url for the file, 
        # since yelp doesn't give us bucket access
        url = client.generate_presigned_url(
                'get_object',
                Params={'Bucket': config['bucket_name'],
                'Key':config['bucket_dir'] +'/'+ filename },
                ExpiresIn=3600 # 1 hour in seconds
                )
        # do the downloading
        logger.info("Feed URL: ", url)
        try:
            download_url_to_file(url, config['rawdata_dir'], config['local_file'])
            # if we succeed, move on
            break

        except Exception:
            # TODO: Throw more explicit exceptions from `download_url_to_file`
            # so we can handle it more explicitly, currenlty it can be misleading
            if day_delta == 30: 
                logger.warning("NO YELP DATA AVAILABLE FOR THE PAST MONTH!")
                return
            else:
                logger.warning("no data for date: %s\n\
                     Trying the day before." % day.strftime("%m/%d/%Y"))

    logger.info("Latest Yelp Data successfully downloaded from feed.")
    # save the success to download history
    ydh.downloaded = True
    db.commit()
    return local_file

def unzip_file(filename):
    """
    Take in a .gz file and unzip it, saving it with the same file name
    """
    # first make sure we haven't already unzipped it
    db = get_db_session()
    ydh = db.query(YelpDownloadHistory).filter(YelpDownloadHistory.date==date.today()).scalar()

    # if it doesn't exist, error out because we need to download it
    if not ydh or not ydh.date == date.today() or not ydh.downloaded:
        logger.critical("Cannot unzip file for today because it wasn't downloaded")
        return

    if ydh.unzipped:
        logger.info("Today's feed already unzipped, skipoing the unzip")
        rawfile = filename.strip('.gz')
        return rawfile

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
    ydh.unzipped = True
    db.commit()
    return rawfile

def upsert_yelpfile_to_db(filename, geocode=True):
    """
    This takes in the JSON file of all of the Yelp businesses and
    all the affiliate data (reviews, categories, etc.) and upserts them to the DB

    It follows the db schema used by the ORM, but doesn't use the ORM directly
    for optimization purposes.  

    Where the ORM would take a week or more (estimated) to upload 
    a completely new file of 35k businesses,
    this version does so in ~= 45 min (w/o geocode and over ethernet)

    DON'T mess with this code unless you know what you're doing.
    Hopefully it's well commented enough for you to figure it out if you need to.
    But it is sensitive (relative to normal model code) because of the amount of
    data that must be transferred to the DB.

    Args:
        filename: the name of the unzipped Yelp JSON filename

        geocode: whether or not to geocode locations missing a Lat/Lon
         - Can slow down the code significantly if it's the first geocode attempt
         - Most Yelp locations don't have Lat/Lons
         - On first upload consider calling the geocode db function after

    Returns:
        None. But the database will be updated :)

    TODO:
        - Add a geocode unkown locations function
        - Check if syndication has already been uploaded today

    """
    # database handler object
    db = get_db_session(echo=False, autoflush=False, autocommit=True)

    # check YelpDownloadHistory to see if we've already uploaded the feed
    ydh = db.query(YelpDownloadHistory).filter(YelpDownloadHistory.date==date.today()).scalar()

    # if it doesn't exist, isnt today, hasn't been downloaded or unzipped
    if not ydh or not ydh.date == date.today() or not ydh.downloaded or not ydh.unzipped:
        logger.critical("Can't upload todays feed if it hasn't been downloaded and unzipped")
        return

    if ydh.uploaded:
        logger.info("Already upserted today's Yelp feed. Skipping")
        return

    # geocoder for businesses w/o lat longs
    geoLocator = Nominatim()

    logger.info("Updating Yelp DB..........")

    # setup list of businesses to skip updating
    # because we've uploaded them since yelp updated them
    # this part gets the skip condition
    newest = db.query(Business).order_by(desc(Business.updated_at)).first()
    
    # check for if there's a business in the db
    if newest:
        most_recent = newest.updated_at
        init_db = False
        logger.info("Last updated: %r" % most_recent.strftime('%m/%d/%Y:%M:%H:%S'))

    # if not, then it's the first time we're populating it
    else:
        logger.info("First Database Population: This could take a looong time...")
        most_recent = None
        init_db = True

    # if we're initializing the db, disable the foreign key constraints
    # this will improve upload speeds
    if init_db and 'mssql' in dbconfig['dbbackend']:
        disable_fk = """
        ALTER TABLE dbo.%s NOCHECK CONSTRAINT fk_loc;
        ALTER TABLE dbo.%s NOCHECK CONSTRAINT fk_biz_id;
        ALTER TABLE dbo.%s NOCHECK CONSTRAINT fk_cat_alias;
        ALTER TABLE dbo.%s NOCHECK CONSTRAINT fk_rev_biz_id;
        """ % ( businesses.name, business_category_table.name,
                business_category_table.name, yelp_reviews.name)
        with db.begin():
            db.execute(disable_fk)


    start_time = time.time() # for timing the whole process

    # get sets of uids for each data model, 
    # so we can quickly determine if a datum needs to be updated or inserted
    # this is much faster than querying the db every time
    with db.begin():
        db_biz_ids = set([ b.id 
                        for b in db.query(Business.id).all() ])
        db_review_ids = set([ r.id 
                            for r in db.query(YelpReview.id).all() ])
        db_locations = set([ l.street_address 
                            for l in db.query(Location.street_address).all() ])
        db_categories = set([ c.alias 
                            for c in db.query(YelpCategory.alias).all() ])
        db_biz_categories = set([ (assoc.business_id, assoc.category_alias) 
                                for assoc in db.query(business_category_table).all()])

    # batch upsert data structures
    unloaded_locations = {}
    unloaded_categories = {}
    insert_businesses = []
    insert_reviews = []
    insert_documents = []
    insert_doc_associations = []
    update_businesses = []
    update_reviews = []
    update_documents = []
    biz_cats = []

    # loop over json file ans upsert all data
    with open(filename, 'rb') as infile: # for unzipped files
        biz_num = 0
        biz_count = 0
        review_count = 0
        upload_mod = 500 # size of batch upload 

        # each business is one line
        for line in infile:
            biz_num += 1
            biz_count +=1
            logger.info("Updating Restaurant #%i...." % biz_num)

            current = time.time()-start_time
            m, s = divmod(current, 60)  
            h, m = divmod(m, 60)
            logger.info("Time so far: %d:%02d:%02d" % (h, m, s))

            # if business doesn't load correctly, skip it
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
                    logger.info("SKIPPING (NOT NEW): %s" % biz['name'])
                    biz_count -=1
                    # print biz_count
                    continue

            # create the Location object
            loc = dict(biz['location'])                     
            street_address = xstr(loc['address'][0])\
                +', ' +xstr(loc['address'][1])\
                +', ' +xstr(loc['address'][2])\
                +', '+xstr(loc['city']) +', '+xstr(loc['state'])\
                +' '+xstr(loc['postal_code'])
            street_address = street_address.lower()

            # haven't encountered this location so make one
            if street_address not in db_locations and street_address not in unloaded_locations.keys():
                try: # some don't have lat,longs
                    location = {
                                'street_address':street_address,
                                'latitude':float(loc['coordinate']['latitude']),
                                'longitude':float(loc['coordinate']['longitude']),
                                'line1':xstr(loc['address'][0]),
                                'line2':xstr(loc['address'][1]),
                                'line3':xstr(loc['address'][2]),
                                'city':xstr(loc['city']),
                                'country':xstr(loc['country']),
                                'postal_code':xstr(loc['postal_code']),
                                'state':xstr(loc['state'])
                                }
                except TypeError: # so they can't get converted to float
                    # so reverse geocode them (if enabled)
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
                    # else ignore the lat/lons
                    else:
                        lat = None
                        lon = None
                    location = {
                                'street_address':street_address,
                                'latitude':lat,
                                'longitude':lon,
                                'line1':xstr(loc['address'][0]),
                                'line2':xstr(loc['address'][1]),
                                'line3':xstr(loc['address'][2]),
                                'city':xstr(loc['city']),
                                'country':xstr(loc['country']),
                                'postal_code':xstr(loc['postal_code']),
                                'state':xstr(loc['state'])
                                }
                # add to running list of unloaded locations
                unloaded_locations[street_address] = location 

            # create the Business Object
            if biz['is_closed'] == 0: is_closed = False
            else: is_closed = True

            # if old business we need to update it
            if biz['id'] in db_biz_ids:
                business = {
                        'id':biz['id'],
                        'name':biz['name'],
                        'phone':biz['phone'],
                        'rating':biz['rating'],
                        'url':biz['url'],
                        'business_url':biz['business_url'],
                        'last_updated':datetime.strptime(biz['time_updated'], "%Y-%m-%dT%H:%M:%S"),
                        'is_closed':is_closed,
                        'location_address':street_address,
                        'updated_at':datetime.now()
                        }
                update_businesses.append(business)
            # else it's new so insert it
            else:
                business = {
                        'id':biz['id'],
                        'name':biz['name'],
                        'phone':biz['phone'],
                        'rating':biz['rating'],
                        'url':biz['url'],
                        'business_url':biz['business_url'],
                        'last_updated':datetime.strptime(biz['time_updated'], "%Y-%m-%dT%H:%M:%S"),
                        'is_closed':is_closed,
                        'location_address':street_address,
                        'updated_at':datetime.now()
                        }
                insert_businesses.append(business)

            # create all of the Reviews
            for i, rev in enumerate(biz['reviews']):
                # if the review isn't new, don't do anything
                # uncomment this code to update it (significant slowdown)
                if rev['id'] in db_review_ids:
                    pass
                    # review = {
                    #         'business_id':biz['id'],
                    #         'text' : rev['text'],
                    #         'rating':rev['rating'],
                    #         'user_name':rev['user']['name'],
                    #         'created':rev['created'],
                    #         'yelp_id':rev['id'],
                    #         'updated_at':datetime.now()
                    #         }
                    # document = {
                    #         'id':rev['id'],
                    #         'type':yelp_reviews.name
                    # }
                    # update_reviews.append(review)
                    # update_documents.append(document)
                # else create a new one
                else:
                    # reviw = YelpReview(
                                # yelp_id=)
                    review = {
                            'business_id':biz['id'],
                            'text' : unicode(rev['text']),
                            'rating':rev['rating'],
                            'user_name':rev['user']['name'],
                            'created':datetime.strptime(rev['created'], '%Y-%m-%d'),
                            'id':rev['id'],
                            # 'doc_id':rev['id'],
                            'doc_assoc_id':rev['id'],
                            'updated_at':datetime.now()
                            }
                    document = {
                            'id':rev['id'],
                            'assoc_id':rev['id'],
                            # 'type':yelp_reviews.name,
                            'created':datetime.now(),
                            'fp_label':None,
                            'mult_label':None,
                            'inc_label':None,
                            'fp_pred':None,
                            'mul_pred':None,
                            'inc_pred':None,
                            'fp_label_time':None,
                            'mult_label_time':None,
                            'inc_label_time':None,
                            'fp_pred_time':None,
                            'mul_pred_time':None,
                            'inc_pred_time':None
                    }
                    doc_assoc = {
                        'assoc_id':rev['id'],
                        'type':yelp_reviews.name
                    }
                    insert_reviews.append(review)
                    insert_documents.append(document)
                    insert_doc_associations.append(doc_assoc)
            review_count += len(biz['reviews'])

            # create the Categories
            for category in biz['categories']:
                # if we it's new create it, provided we haven't already
                if (category['alias'] not in db_categories 
                and category['alias'] not in unloaded_categories.keys()):
                    # some aliases are bad, so skip them
                    if (xstr(category['alias']) == '' 
                    or xstr(category['alias']) == None): 
                        logger.warning("BAD CATEGORY %r... Skipping" % xstr(category['alias']))
                        continue
                    cat = {'alias':xstr(category['alias']),
                            'title':xstr(category['title'])
                          }
                    unloaded_categories[category['alias']] = cat
                # create the business association link
                assoc = {
                         'business_id':biz['id'], 
                         'category_alias':category['alias']
                         }
                if (assoc['business_id'], assoc['category_alias']) not in db_biz_categories:
                    biz_cats.append(assoc)

            # if we've reached batch size, perform the actual transactions
            if biz_count % upload_mod == 0:
                with db.begin():
                    logger.info("Uploading Batch of %i to DB...." % upload_mod)
                    logger.info("Uploading Locations to DB....")
                    db.bulk_insert_mappings(Location, unloaded_locations.values())
                    logger.info("Uploading Yelp Categories to DB....")
                    db.bulk_insert_mappings(YelpCategory, unloaded_categories.values())
                    bizlen = len(insert_businesses) + len(update_businesses)
                    logger.info("Uploading %i Businesses to DB...." %bizlen)
                    db.execute(businesses.insert(), insert_businesses)
                    db.bulk_update_mappings(Business, update_businesses)
                    revlen = len(insert_reviews) + len(update_reviews)
                    logger.info("Uploading %i Documents to DB...." % revlen)
                    db.execute(document_associations.insert(), sorted(insert_doc_associations, key=lambda x:x['assoc_id']))
                    db.execute(documents.insert(), sorted(insert_documents, key=lambda x:x['id']))
                    # db.bulk_update_mappings(Document, update_documents)
                    logger.info("Uploading %i Business Reviews to DB...." % revlen)
                    db.execute(yelp_reviews.insert(), sorted(insert_reviews, key=lambda x:x['id']))
                    # db.bulk_update_mappings(YelpReview, update_reviews)
                    #there seem to be duplicate categories for a business
                    #so make the associations unique
                    logger.info("Uploading Business Category associations to DB....")
                    biz_cats = [dict(tupleized) for tupleized in set(tuple(assoc.items()) for assoc in biz_cats)]
                    db.execute(business_category_table.insert(), biz_cats)

                # reset the lists for the next batch
                db_categories.update(unloaded_categories.keys())
                db_locations.update(unloaded_locations.keys())
                unloaded_categories = {}
                unloaded_locations = {}
                insert_businesses = []
                insert_reviews = []
                insert_documents = []
                insert_doc_associations = []
                update_businesses = []
                update_reviews = []
                update_documents = []
                biz_cats = []

    # upload the final batch
    bizlen = len(insert_businesses) + len(update_businesses)
    if bizlen > 0:
        with db.begin():
            logger.info("Uploading Batch of %i to DB...." % upload_mod)
            logger.info("Uploading Locations to DB....")
            db.bulk_insert_mappings(Location, unloaded_locations.values())
            logger.info("Uploading Yelp Categories to DB....")
            db.bulk_insert_mappings(YelpCategory, unloaded_categories.values())
            bizlen = len(insert_businesses) + len(update_businesses)
            logger.info("Uploading %i Businesses to DB...." %bizlen)
            db.execute(businesses.insert(), insert_businesses)
            db.bulk_update_mappings(Business, update_businesses)
            revlen = len(insert_reviews) + len(update_reviews)
            logger.info("Uploading %i Documents to DB...." % revlen)
            db.execute(document_associations.insert(), sorted(insert_doc_associations, key=lambda x:x['assoc_id']))
            db.execute(documents.insert(), sorted(insert_documents, key=lambda x:x['id']))
            # db.bulk_update_mappings(Document, update_documents)
            logger.info("Uploading %i Business Reviews to DB...." % revlen)
            db.execute(yelp_reviews.insert(), sorted(insert_reviews, key=lambda x:x['id']))
            # db.bulk_update_mappings(YelpReview, update_reviews)
            #there seem to be duplicate categories for a business
            #so make the associations unique
            logger.info("Uploading Business Category associations to DB....")
            biz_cats = [dict(tupleized) for tupleized in set(tuple(assoc.items()) for assoc in biz_cats)]
            db.execute(business_category_table.insert(), biz_cats)
    
    # if we are initializing the db, we need to reenable the fk constraints
    # because we put in all the data correctly, we are sure the fks are correct
    # this will error if they aren't
    if init_db and 'mssql' in dbconfig['dbbackend']:
        # put back all the constraints
        logger.info("Cheking Constraints...")
        enable_fk = """
        ALTER TABLE dbo.%s CHECK CONSTRAINT ALL;
        ALTER TABLE dbo.%s CHECK CONSTRAINT ALL;
        ALTER TABLE dbo.%s CHECK CONSTRAINT ALL;
        ALTER TABLE dbo.%s CHECK CONSTRAINT ALL;
        """ % ( businesses.name, business_category_table.name,
                business_category_table.name, yelp_reviews.name)
        with db.begin():
            db.execute(enable_fk)
    total_time = float(time.time() - start_time)
    logger.info("Upserted %i businesses and %i total reviews in %d seconds = %.2f minutes" %\
                 (biz_num, review_count, total_time,  total_time/60.))

    # update the download history
    with db.begin():
        ydh.uploaded = True
    
        

from random import shuffle # to shuffle list in place

def geocodeUnknownLocations(wait_time=2, run_time=240):
    """
    Geocode any locations that don't have Lat/Lons

    Only do so for up to `run_time` minutes, because this can take a very long time if most are unknown

    Also shuffle so that they all get equal probability of being tried

    Args:
        wait_time: how long to wait until timeout

    Returns: 
        None

    """
    geoLocator = Nominatim()
    # print geoLocator.geocode("548 riverside dr., NY, NY, 10027") # test
    db = get_db_session()
    unknowns = db.query(Location).filter(Location.latitude==None).all()
    shuffle(unknowns) # give them all a fighting chance
    logger.info("Attempting to geocode random unknown locations for %i minutes" % run_time)
    logger.info("%i Unkown locations to geocode" % len(unknowns))
    locations = []
    upload_mod = 100 # upload batch size

    start_time = time.time()
    run_time *= 60 # turn it into seconds

    for i, location in enumerate(unknowns):
        # max try time stopping criterion
        if (time.time() - start_time) > run_time:
            logger.info("Max geocoding time has elapsed... Stopping for this run")
            db.add_all(locations)
            db.commit()
            break
        # print location.street_address
        logger.info("Geocoding location %i..." % i)
        try:
            geo = geoLocator.geocode(location.street_address, timeout=wait_time)
            lat = geo.latitude
            lon = geo.longitude
            logger.info("\tSuccess!")
        except Exception as e:
            # print  "Exception: ", e
            logger.warning("\tGeocode failed, assigning NULL Lat/Long")
            lat = None
            lon = None
        location.latitude = lat
        location.longitude = lon
        locations.append(location)
        if i % upload_mod == 0:
            db.add_all(locations)
            db.commit()
            locations = []
    logger.info("Finished geocode attempts")



