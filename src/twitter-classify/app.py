import json
import schedule
import time
from pymongo import MongoClient
from pymongo import UpdateOne
from itertools import islice
from sklearn.externals import joblib

twitter_sick_classifier = joblib.load("final_twitter_models/best_lr_sick_silver.pkl")

def make_batches(n, iterable):
	i = iter(iterable)
	piece = list(islice(i, n))
	while piece:
		yield piece
		piece = list(islice(i, n))



def getTweets(db):
	return db.tweets.find({"classification" : { "$exists" : False }})

def classify(batch =10000):
	client = MongoClient('mongodb://mongo:27017/')   
	db = client.fdbnyc
	tweets = getTweets(db)
	for batch in make_batches(batch, tweets):
		texts = [ x["full_text"] for x in batch]
		sick_preds_pos_probs = twitter_sick_classifier.predict_proba(texts)[:,1] 
		tweet_requests=[]
		for i, tweet in enumerate(batch):
			sick_score=sick_preds_pos_probs[i]
			classification ={ "total_score":sick_score }
			update = {"$set": {"classification" : classification }}
			tweet_requests.append(UpdateOne({"_id": tweet["_id"]}, update ))
		db.tweets.bulk_write(tweet_requests,ordered=False)


if __name__ == '__main__':
	schedule.every().hour.do(classify)
	while True:
		schedule.run_pending()
		time.sleep(1)
