from time import sleep
from pymongo import UpdateOne




def search(twitter_api, query, since_id):
	parameters={'q': query ,'count': 100 ,'lang':'en','tweet_mode': 'extended', 'since_id': since_id, 'geocode': '40.6700,-73.9400,53mi'}
	query_result=[]
	while True:
		try: 
			result=twitter_api.search(**parameters)
			query_result.extend(result['statuses'])
			sleep(2)
			try:
				next_results_url_params = result['search_metadata']['next_results']
				parameters['max_id'] = next_results_url_params.split('max_id=')[1].split('&')[0]
			except:
				break
		except Exception as e:
			print(e)
			sleep(60)
	return query_result


def run_queries(twitter_api, queries, db):
	def rename_id(obj):
		obj["_id"]=obj["id"]
		del obj["id"]
		return obj
	def add_source(obj):
		obj["tweet_source"]='SEARCH_FOODBORNE_ILLNESS'
		return obj
	
	while True:
		for query in queries:
			try:
				max_query_id = db.query_max_id.find_one({'_id': query})
				since_id = max_query_id['max_id'] if max_query_id else -1
				tweets = [add_source(rename_id(x)) for x in  search(twitter_api, query, since_id) if 'retweeted_status' not in x]
				if tweets:
					twitter_upserts=[UpdateOne({'_id':tweet['_id']}, {"$set": tweet},upsert=True) for tweet in tweets]
					db.tweets.bulk_write(twitter_upserts,ordered=False)
					new_max_id={ 'max_id': tweets[0]['_id']}
					db.query_max_id.update_one({'_id': query},{"$set":new_max_id}, upsert=True)
			except Exception as e:
				print(e, flush=True)
				sleep(60)