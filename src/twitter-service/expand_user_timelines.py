from time import sleep
from datetime import datetime

def expand_user(twitter_api,user_id,parameters):
	for i in range(2):
		try:
			query={**{'user_id':user_id,'tweet_mode': 'extended','count':10}, **parameters}
			sleep(0.4)
			return twitter_api.get_user_timeline(**query)
		except Exception as e:
			print(e)
			sleep(60)
	return []

def expand_user_timelines(twitter_api, db):
	def add_source(obj):
		obj["tweet_source"]='EXPANSION_USER_TIMELINE'
		return obj
	
	while True:
		query={'timelineExpansionAttemptedDate':{'$exists': False}}
		tweetstoexpand = db.tweets.find(query)
		for tweet in tweetstoexpand:
			user_id = tweet['user']['id']
			tweet_id = tweet['_id']
			tweets_after=expand_user(twitter_api,user_id,{'since_id':tweet_id})
			tweets_before=expand_user(twitter_api,user_id,{'max_id':tweet_id-1})
			tweets = [add_source(x) for x in tweets_before+tweets_after if 'retweeted_status' not in x]
			update_expansion={"$set":{'timelineExpansionAttemptedDate': datetime.utcnow() }}
			if tweets:
				update_expansion["$push"]={"relatedTweets": {"$each": tweets}}
			db.tweets.update_one({'_id':tweet['_id']},update_expansion)
