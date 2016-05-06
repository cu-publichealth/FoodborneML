from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sklearn.externals import joblib
from foodbornenyc.settings import yelp_classify_config as config
from operator import attrgetter
from foodbornenyc.models.models import get_db_session
from foodbornenyc.models.documents import YelpReview, documents
from foodbornenyc.models.businesses import Business, businesses
from foodbornenyc.UI.reviewclasses import Review, UIYelpReview, UIBusiness

from foodbornenyc.util.util import get_logger, sec_to_hms


from flask import Flask
from flask import render_template
from flask_table import Table, Col, ButtonCol



def get_yelp_sick_reviews(echo):
    db = get_db_session(echo=echo, autoflush=False, autocommit=True)
    count = 0
    ## Construct query to get all positive reviews
    with db.begin():
        high_scores = select([documents.c.id]).where(documents.c.fp_pred > .5)     
        query = (db.query(YelpReview).filter(YelpReview.id.in_(high_scores)).order_by(YelpReview.id.asc()))
        ## Line below gets count of reviews meeting criteria
        ##count = (db.execute(select([func.count(documents.c.id)]).where(documents.c.fp_pred > .5)).scalar())
        ##print count
    offset = 0
    reviews = []
    ## Collect all reviews meeting query criteria
    while True:
        returned = False
        try:
            with db.begin():
                for i, review in enumerate(query.limit(100).offset(offset)):
                    returned = True
                            
                    business_query = db.query(Business).filter(Business.id.in_(select([businesses.c.id]).where(
                            businesses.c.id == review.business_id)))
                    for j, business in enumerate(business_query.limit(1).offset(0)):
                        business = UIBusiness(business.id, business.name, business.phone, business.rating, business.url, business.business_url)
                        print business.business_url
                        reviews.append(UIYelpReview(business, review.text, "%.3f" % review.document.fp_pred, review.document.created, "Yelp", review.user_name, review.id))
        except OperationalError:
            break
        offset += 100
        if not returned:
            break

    ## Sort reviews and render table, high to low
    reviews = sorted(reviews, key=attrgetter('score'), reverse=True)

    ## Make a flask table and return it

    ##return ReviewTable(reviews)
    return reviews
