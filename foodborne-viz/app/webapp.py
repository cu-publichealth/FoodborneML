import tornado.ioloop
import tornado.web
from tornado.log import enable_pretty_logging
import os
import json
from pymongo import MongoClient
from bson.json_util import dumps
import datetime
from motor.motor_tornado import MotorClient
global data, db

enable_pretty_logging()
reviews_with_sentence_errors = {}
client = MotorClient(os.environ['URI'])


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('html/geo_map.html', API_KEY=os.environ['GOOGLE_MAPS_API_KEY'])


class RestaurantHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            business_id = self.get_argument('business_id')
            start_time = self.get_argument('start_time')
            end_time = self.get_argument('end_time')
            review_bottom_threshold = self.get_argument('review_bottom_threshold')
            review_top_threshold = self.get_argument('review_top_threshold')
            self.render('html/restaurant.html',
                        start_time=start_time,
                        end_time=end_time,
                        review_bottom_threshold=review_bottom_threshold,
                        review_top_threshold=review_top_threshold,
                        business_id=business_id)
        except Exception as e:
            print("Exception in rendering", e)
            self.write('Error')


class GetRestuarantInfo(tornado.web.RequestHandler):
    async def get(self):
        id = self.get_query_argument('business_id')
        info = await get_rest_info(id)
        json_string = dumps(info, ensure_ascii=False).encode('utf8')

        if info:
            try:
                self.write(json_string)
            except Exception as e:
                print("Error writing info", e)
                self.write("Error")
        else:
            self.write("Error")


class GetReviews(tornado.web.RequestHandler):
    def get(self):
        try:
            print("get received", datetime.datetime.now())
            self.write(data)
            print("get returned", datetime.datetime.now())
        except Exception as e:
            print("Exception", e)
            self.write("Error: " + str(e))


class UpdateReviews(tornado.web.RequestHandler):
    async def get(self):
        await get_newest_reviews()
        self.write("Completed")



class ReviewSentenceError(tornado.web.RequestHandler):
    def post(self):
        try:
            review_id = self.get_argument('review_id')
            to_insert = {
                'review_id': review_id,
                'sentences_split_length': self.get_argument('sentences_split_length'),
                'sentence_scores_length': self.get_argument('sentence_scores_length')
            }
            global reviews_with_sentence_errors
            if review_id not in reviews_with_sentence_errors:
                reviews_with_sentence_errors[review_id] = to_insert
        except Exception as e:
            print("Error adding faulty sentence", e)


class GetReviewsWithSentenceErrors(tornado.web.RequestHandler):
    def get(self):
        self.write(dumps(reviews_with_sentence_errors))


async def get_newest_reviews():
    print("Querying DB...", datetime.datetime.now())
    db = client[os.environ['DB']]
    try:
        collection = db[os.environ['COLLECTION_NEWEST_MERGED_REVIEWS']]
        cursor = collection.find({})
        docs = await cursor.to_list(length=30000)
    except Exception as e:
        print("could not reload data:", e)
        docs = []

        return False

    try:
        docs = dumps(docs)
        global data
        data = docs
        print("Data updated", datetime.datetime.now())
        try:
            with open('get_reviews.json', 'w') as f:
                f.write(data)
        except IOError as e:
            print("did't write to file", e)

        return True
    except Exception as e:
        print("couldn't update data", e, datetime.datetime.now())

        return False


def load_initial_data():
    try:
        with open('get_reviews.json', 'r') as f:
            global data
            data = f.read()
            return True
    except IOError as e:
        print(e)
        return False


def init_mongo():
    try:
        client = MotorClient(os.environ['URI'])
    except Exception as e:
        print("Error connecting to db", e)


async def get_rest_info(id):
    db = client[os.environ['DB']]
    try:
        collection = db['businesses']
        result = collection.aggregate([
            {
                '$match': {
                    '_id': id
                },
            },
            {
                '$lookup': {
                    'from': os.environ['COLLECTION_ALL_SICK_REVIEWS'],
                    'localField': '_id',
                    'foreignField': 'business_id',
                    'as': 'reviews'
                }
            }
        ])
        x = await result.to_list(length=1)
        if len(x) > 0:
            return x[0]
        return None
    except Exception as e:
        print("Exception", e)
        return None


def make_app():
    pwd = os.getcwd()
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/log_sentence_error", ReviewSentenceError),
        (r"/get_sentence_errors", GetReviewsWithSentenceErrors),
        (r"/restaurant_info", RestaurantHandler),
        (r"/get_reviews", GetReviews),
        (r"/get_restaurant_info", GetRestuarantInfo),
        (r"/update_data", UpdateReviews),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": pwd + "/datafiles/"}),
        (r"/images/(.*)", tornado.web.StaticFileHandler, {"path": pwd + "/datafiles/images"}),
        (r"/css/(.*)", tornado.web.StaticFileHandler, {"path": pwd + "/css/"}),
        (r"/js/(.*)", tornado.web.StaticFileHandler, {"path": pwd + "/js/"})
    ], client=client)


if __name__ == "__main__":
    app = make_app()
    if not load_initial_data():
        tornado.ioloop.IOLoop.current().run_sync(get_newest_reviews)

    app.listen(int(os.environ['WEBAPP_PORT']))
    print('running')
    tornado.ioloop.IOLoop.current().start()