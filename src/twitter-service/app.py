from twython import Twython
from pymongo import MongoClient
from run_queries import run_queries
from expand_user_timelines import expand_user_timelines
from expand_user_conversations import expand_user_conversations
import configparser
import threading
import logging



def search_config():
	config=configparser.ConfigParser()
	config.read('twitter.ini')
	twitter_config=config['TWITTER']
	return {'app_key': twitter_config['consumer_key'],
			'app_secret': twitter_config['consumer_secret']}

def getTwitter():
	config=search_config()
	access_token=Twython(**config, oauth_version=2).obtain_access_token()
	return Twython(config['app_key'], access_token=access_token)







if __name__ == '__main__':
	twitter_api=getTwitter()
	queries = ['#foodpoisoning','#stomachache','"food poison"','"food poisoning"','stomach','vomit','puke','diarrhea','"the runs"']
	client = MongoClient('mongodb://mongo:27017/')
	db = client.fdbnyc
	threading.Thread(target=run_queries,args=(twitter_api, queries, db)).start()
	threading.Thread(target=expand_user_timelines,args=(twitter_api,db)).start()
	threading.Thread(target=expand_user_conversations,args=(twitter_api,db)).start()
