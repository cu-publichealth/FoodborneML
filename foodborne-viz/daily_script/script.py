import sys
import os
import schedule
import time
from update_locs import add_location_data
from pymongo import MongoClient
import requests


def connect_and_update_db():
    db_name = os.environ['DB']
    collection_restaurants = os.environ['COLLECTION_RESTAURANTS_JOIN_EXTRA_FIELD']
    collection_lat_long = os.environ['COLLECTION_RESTAURANTS_EXTRA_FIELD']

    db_not_active = True
    while(db_not_active):
        try:
            client = MongoClient(os.environ['URI'])
            db_not_active = False
        except Exception as e:
            print('Error while connecting to DB: ', e)
            print('trying again...')
            time.sleep(10)
        else:
            try:
                db = client[db_name]
                collection_restaurants = db[collection_restaurants]
                collection_lat_long = db[collection_lat_long]
                num_edited = add_location_data(collection_restaurants, collection_lat_long)
                print(num_edited, "docs edited")
            except Exception as e:
                print("add location error:", e)


def update_webapp_data():
    port = os.environ.get('WEBAPP_PORT')
    if port:
        try:
            requests.get('http://webapp:' + str(port) + '/update_data')
            print("updated database dump")
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print("didn't work yet")



if __name__ == '__main__':
    schedule.every().day.do(connect_and_update_db)
    schedule.every().day.do(update_webapp_data)
    connect_and_update_db()
    while True:
        schedule.run_pending()
        time.sleep(1)
