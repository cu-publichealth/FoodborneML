from pymongo import MongoClient


def on_starting(server):
    client = MongoClient('mongodb://mongo:27017/')
    db = client.fdbnyc
    db.yelp_ack.drop()
    db.yelp_feed.create_index("business_id",background=True)