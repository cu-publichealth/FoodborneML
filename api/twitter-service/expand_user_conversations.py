from time import sleep
from datetime import datetime

import logging

logger = logging.getLogger(__name__)

def expand_conversation(twitter_api,tweet_id):
	for i in range(2):
		try:
			query={'tweet_mode': 'extended','id':tweet_id}
			sleep(1)
			return twitter_api.show_status(**query)
		except Exception as e:
			logger.warning('Exception while getting conversation tweet', exc_info=True)
			sleep(60)
	return None

def expand_user_conversations(twitter_api, db):
	def add_source(obj):
		obj["tweet_source"]='EXPANSION_CONVERSATION'
		return obj
	
	while True:
		try:
			query={'conversationTrackingAttemptedDate':{'$exists': False}}
			tweetstoexpand = db.tweets.find(query)
			for tweet in tweetstoexpand:
				tweet_id = tweet['_id']
				update_expansion={}
				if tweet['in_reply_to_status_id']:
					reply_to_id=tweet['in_reply_to_status_id']
					new_tweet=expand_conversation(twitter_api, reply_to_id)
					if new_tweet:
						new_tweet=add_source(new_tweet)
						update_expansion["$push"]={"relatedTweets":new_tweet}

				update_expansion["$set"]={'conversationTrackingAttemptedDate': datetime.utcnow() }
				db.tweets.update_one({'_id':tweet['_id']},update_expansion)
		except Exception as e:
			logger.warning('Exception while expanding conversations', exc_info=True)
			sleep(60)