import configparser
import boto3
import urllib.request
import os
import gzip
import json
import schedule
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from pymongo import MongoClient
from pymongo import UpdateOne

config=configparser.ConfigParser()
config.read('yelp.ini')
yelp_config=config['YELP']

        
s3 = boto3.client('s3',
                   aws_access_key_id=yelp_config["aws_access_key_id"],
                   aws_secret_access_key=yelp_config["aws_secret_key_id"],
                  )
				

def gettolerance(db):
	if ("yelp_history" not in db.collection_names()) or (db.yelp_history.count()==0) :
		return 30
	else:
		newest=db.yelp_history.find_one(sort=[("date", -1)])["date"].date()
		time_delta=date.today()-newest
		return min(30,time_delta.days)

def getfeed(day):
	day_str = day.strftime('%Y%m%d')
	url = s3.generate_presigned_url(
    	ClientMethod='get_object',
    		Params={
        		'Bucket': yelp_config["bucket"],
        		'Key': yelp_config["bucket_dir"]+'/'+day_str+yelp_config["extension"]},
        	ExpiresIn=3600
	)
	filename=day_str+yelp_config["extension"]
	urllib.request.urlretrieve(url,filename)
	return filename

def getfeedwithtolerance(tolerance):
	day = date.today()
	for day_delta in range(tolerance):
		day = date.today() - timedelta(day_delta)
		try:
			return day,getfeed(day)
		except Exception as e:
			print(e)
			continue
	return None

def process_business(business):
	def inject_business_id(review):
		review['business_id'] = business['id']
		return review
	def project_id(document):
		document['_id']=document['id']
		del document['id']
		return document
	reviews = [ project_id(inject_business_id(review)) for review in business['reviews']]
	del business['reviews']
	return (reviews, project_id(business))


def upsertyelp(db,filename):
	with gzip.open(filename,'rb') as f:
		business_requests = []
		review_requests = []
		for number,line in enumerate(f):
			(reviews,business)=process_business(json.loads(line))
			business_requests.append(UpdateOne({'_id':business['_id']}, {"$set":business},upsert=True))
			review_requests.extend([ UpdateOne({'_id':review['_id']}, {"$set": review},upsert=True) for review in reviews])
			if len(business_requests)>10000:
				db.businesses.bulk_write(business_requests,ordered=False)
				business_requests=[]
			if len(review_requests)>10000:
				db.reviews.bulk_write(review_requests,ordered=False)
				review_requests=[]
		db.businesses.bulk_write(business_requests,ordered=False)
		db.reviews.bulk_write(review_requests,ordered=False)
	os.remove(filename) 

def checkyelp():
	client = MongoClient('mongodb://mongo:27017/')   
	db = client.fdbnyc
	feed = getfeedwithtolerance(gettolerance(db))
	if feed:
		(day,filename)=feed
		withtime=datetime.combine(day, datetime.min.time())
		upsertyelp(db,filename)
		db.yelp_history.insert_one({"date": withtime})    


if __name__ == '__main__':
	schedule.every().day.at("23:00").do(checkyelp)
	while True:
		schedule.run_pending()
		time.sleep(1)