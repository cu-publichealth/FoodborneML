from flask import Flask
from flask import Response 
from flask import jsonify
from flask_httpauth import HTTPBasicAuth
from bson import json_util
from pymongo import MongoClient
import re

client = MongoClient('mongodb://mongo:27017/')
db = client.fdbnyc

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "user": "user"
}

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

def tojsonstream(x):
	yield '['
	for i, item in enumerate(x):
		if i==0:
			yield json_util.dumps(item)
		else:
			yield ','+json_util.dumps(item)
	yield ']'



@app.route('/new/businesses')
@auth.login_required
def newyelp():

	def lookup():
		return {"$lookup" : { "from" :"yelp_feed", "localField":"_id", "foreignField": "business_id", "as": "reviews"}}

	def keep_new():
		condition_review={"$ne" : [ "$reviews" , [] ]}
		condition_ack ={"$ne": ["$time_updated", "$acknowledged"]}
		condition = {"$or": [condition_review,condition_ack ]}
		if_else = {"if": condition , "then": "$$KEEP", "else": "$$PRUNE"}
		return {"$redact": {"$cond": if_else}}
	
	def project():
		fields={"reviews.business_id":0 , "acknowledged":0 }
		return {"$project":fields}
	
	def change_id(business):
		def rename_id(obj):
			obj["id"]=obj["_id"]
			del obj["_id"]
			return obj
		
		business=rename_id(business)
		business["reviews"]= [rename_id(x) for x in business["reviews"]]
		return business

	
	def acknowldege_record(business):
		review_ids=[review["id"] for review in business["reviews"]]
		record={"_id":business["id"], "time_updated":business["time_updated"],"review_ids": review_ids }
		db.yelp_ack.update_one({"_id":business["id"] },{"$set": record},upsert=True)
		return business
	
	
	pipeline=[lookup(), keep_new(), project(), {"$limit": 100}]
	businesses = db.businesses.aggregate(pipeline)
	businesses_proj=map(change_id,businesses)
	businesses_ack= map(acknowldege_record,businesses_proj)
	return Response(
   		tojsonstream(businesses_ack),
   		mimetype='application/json'
	)

@app.route('/new/tweets')
@auth.login_required
def newtweets():

	def user_mention():
		return {
			'id':'$$mention.id_str',
			'name': '$$mention.name',
			'location':None,
			'screenName':'$$mention.screen_name',
			'is_nyc':None 
		}

	def project_tweet(top=""):
		return {
			'id':f'${top}id_str',
			'createdDate':f'${top}created_at',
			'text':f'${top}full_text',
			'source':f'${top}tweet_source',
			'lattitude': { "$arrayElemAt": [ f"${top}coordinates.coordinates", 1 ]},
			'longitude': { "$arrayElemAt": [ f"${top}coordinates.coordinates", 0 ]},
			'hashtags' :{"$map":{ "input":f'${top}entities.hashtags', "as": "hashtag","in": "$$hashtag.text" }},
			'symbols': {"$map":{ "input":f'${top}entities.symbols', "as": "symbol","in": "$$symbol.text" }},
			'urls': {"$map":{ "input":f'${top}entities.urls', "as": "url","in": "$$url.expanded_url" }},
			'user':{'id': f'${top}user.id_str','name': f'${top}user.name','screenName':f'${top}user.screen_name', 
					'location':f'${top}user.location'},
			'inReplytoTweetId':f'${top}in_reply_to_status_id_str',
			'userMentions': { "$map": { "input": f'${top}entities.user_mentions', "as": "mention", "in": user_mention()}},
		}
	
	def projection():
		return {**project_tweet(), **{'serializedFoursquareCheckin':None,
				'foursquareCheckinAttemptedDate':None,
				'timelineExpansionAttemptedDate':{ "$dateToString": { "format":"%Y-%m-%d %H:%M:%S:%L", "date": "$timelineExpansionAttemptedDate" } },
				'conversationTrackingAttemptedDate':{ "$dateToString": { "format":"%Y-%m-%d %H:%M:%S:%L", "date": "$conversationTrackingAttemptedDate" } },
				'classification':1,
				'relatedTweets': {"$map": {"input": "$relatedTweets", "as": "tweet", "in": project_tweet("$tweet.") }},
				'_id':0}}

	def is_nyc(user):
		locations=['Brooklyn','Hoboken','NY','Manhattan','New York','Bronx','Queens','Long Island','Staten Island']
		user_location=user['location']
		return any([re.search(x, user_location) for x in locations])
	
	def process_tweet(tweet):
		user=tweet['user']
		user['is_nyc']=is_nyc(user)
		tweet['serializedHashtags']=json_util.dumps(tweet['hashtags'])
		del tweet['hashtags']
		tweet['serializedSymbols']=json_util.dumps(tweet['symbols'])
		del tweet['symbols']
		tweet['serializedUrls']=json_util.dumps(tweet['urls'])
		del tweet['urls']
		if 'relatedTweets' in tweet and tweet['relatedTweets']: 
			tweet['serialized_data']=json_util.dumps([process_tweet(x) for x in tweet['relatedTweets']])
			del tweet['relatedTweets']
		elif 'relatedTweets' in tweet:
			tweet['serialized_data']=json_util.dumps([])
			del tweet['relatedTweets']
		return tweet
	
	query={"acknowledged" : { "$exists" : False }, "classification" : { "$exists" : True }, 
							'timelineExpansionAttemptedDate': { "$exists" : True }, 'conversationTrackingAttemptedDate': { "$exists" : True } }
	pipeline=[{"$match": query},{"$project": projection()},{"$limit": 100}]
	items = map(process_tweet, db.tweets.aggregate(pipeline))
	return Response(
    	tojsonstream(items),
    	mimetype='application/json'
	)

@app.route('/ack/business/<id>', methods=['POST'])
@auth.login_required
def ackbusiness(id):
	ack_record=db.yelp_ack.find_one_and_delete({"_id":id})
	if not ack_record:
		return jsonify({"message":"There is nothing to acknowldge for the requested business id"}), 404
	db.businesses.update_one({"_id":id}, {"$set": {"acknowledged":ack_record["time_updated"]}} )
	db.reviews.update_many({"_id":{"$in": ack_record["review_ids"]}},{"$set": {"acknowledged":True}})
	db.yelp_feed.delete_many({"_id":{"$in": ack_record["review_ids"]}})
	return jsonify({"message":"Success"})


@app.route('/ack/tweet/<int:id>', methods=['POST'])
@auth.login_required
def acktweet(id):
	update_result = db.tweets.update_one({"_id":id}, {"$set": {"acknowledged":True}})
	if update_result.matched_count==0:
		return jsonify({"message":"Tweet not found"}),404
	return jsonify({"message":"Success"})

if __name__ == '__main__':
	app.run()
