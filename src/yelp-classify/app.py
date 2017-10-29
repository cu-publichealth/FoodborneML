import json
import schedule
import time
from pymongo import MongoClient
from pymongo import UpdateOne
from itertools import islice
from sklearn.externals import joblib

yelp_sick_classifier = joblib.load("final_yelp_models/final_yelp_sick_model.gz")
yelp_mult_classifier = joblib.load("final_yelp_models/final_yelp_mult_model.gz")

def make_batches(n, iterable):
	i = iter(iterable)
	piece = list(islice(i, n))
	while piece:
		yield piece
		piece = list(islice(i, n))



def getreviews(db):
	return db.reviews.find({"classification" : { "$exists" : False }})

def classify(batch =10000):
	client = MongoClient('mongodb://mongo:27017/')   
	db = client.fdbnyc
	reviews = getreviews(db)
	for batch in make_batches(batch, reviews):
		texts = [ x["text"] for x in batch]
		sick_preds_pos_probs = yelp_sick_classifier.predict_proba(texts)[:,1] 
		mult_preds_pos_probs = yelp_mult_classifier.predict_proba(texts)[:,1]
		review_requests=[]
		for i, review in enumerate(batch):
			sick_score=sick_preds_pos_probs[i]
			mult_score=mult_preds_pos_probs[i] if sick_score>=0.5 else 0
			classification ={ "total_score":(sick_score+mult_score)/2 }
			update = {"$set": {"classification" : classification }}
			review_requests.append(UpdateOne({"_id": review["_id"]}, update ))
		db.reviews.bulk_write(review_requests,ordered=False)
		db.yelp_feed.bulk_write(review_requests,ordered=False)


if __name__ == '__main__':
	schedule.every().day.at("00:00").do(classify)
	while True:
		schedule.run_pending()
		time.sleep(1)
