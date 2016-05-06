from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sklearn.externals import joblib
from foodbornenyc.settings import yelp_classify_config as config
from operator import attrgetter
from foodbornenyc.models.models import get_db_session
from foodbornenyc.models.documents import YelpReview, Tweet, documents
from foodbornenyc.models.businesses import Business, businesses
from foodbornenyc.UI.reviewclasses import Review, UITwitterReview, UIBusiness

from foodbornenyc.util.util import get_logger, sec_to_hms


from flask import Flask
from flask import render_template
from flask_table import Table, Col, ButtonCol


def get_twitter_sick_reviews(echo):
    db = get_db_session(echo=echo, autoflush=False, autocommit=True)
    count = 0
    ## Construct query to get all positive reviews
    with db.begin():
        all_tweets = select([documents.c.id])
        query = (db.query(Tweet).filter(Tweet.id.in_(all_tweets)).order_by(Tweet.id.asc()))
        ## Line below gets count of reviews meeting criteria
        ##count = (db.execute(select([func.count(documents.c.id)]).where(documents.c.fp_pred > .5)).scalar())
        ##print count
    offset = 0
    tweets = []
    ## Collect all reviews meeting query criteria
    while True:
        returned = False
        try:
            with db.begin():
                for i, review in enumerate(query.limit(100).offset(offset)):
                    returned = True
                            
                    #business_query = db.query(Business).filter(Business.id.in_(select([businesses.c.id]).where(
                            #businesses.c.id == review.business_id)))
                    #for j, business in enumerate(business_query.limit(1).offset(0)):
                    business = UIBusiness("Unknown business", "XXX", "XXX", "X", "twitter.com", "twitter.com")
                    tweets.append(UITwitterReview(business, review.text, review.document.fp_pred, review.document.created, "Twitter", review.user_id, review.id))
        except OperationalError:
            break
        offset += 100
        if not returned:
            break

    ## Sort reviews and render table, high to low
    tweets = sorted(tweets, key=attrgetter('score'), reverse=True)

    ## Make a flask table and return it

    ##return ReviewTable(reviews)
    return tweets