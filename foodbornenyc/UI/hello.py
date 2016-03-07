from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sklearn.externals import joblib
from foodbornenyc.settings import yelp_classify_config as config
from operator import attrgetter
from foodbornenyc.models.models import get_db_session
from foodbornenyc.models.documents import YelpReview, documents
from foodbornenyc.models.businesses import Business, businesses

from foodbornenyc.util.util import get_logger, sec_to_hms


from flask import Flask
from flask import render_template
from flask_table import Table, Col

class ReviewTable(Table):
    business_id = Col('Business ID')
    review = Col('Review')
    score = Col('Score')


class Review(object):
    def __init__(self, business_id, review, score):
        self.business_id = business_id     
        self.review = review
        self.score = score


app = Flask(__name__)

@app.route("/")
def hello():
        return "Hello World!"

@app.route('/yelp/')
def yelp():
    echo = False
    db = get_db_session(echo=echo, autoflush=False, autocommit=True)
    count = 0
    ## Construct query to get all positive reviews
    with db.begin():
        high_scores = select([documents.c.id]).where(documents.c.fp_pred > .5)     
        query = (db.query(YelpReview).filter(YelpReview.id.in_(high_scores)).order_by(YelpReview.id.asc()))
        ## Line below gets count of reviews meeting criteria
        ## count = (db.execute(select([func.count(documents.c.id)]).where(documents.c.fp_pred > .5)).scalar())

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
                        businessName= business.name
                        reviews.append(Review(businessName, review.text, review.document.fp_pred))
        except OperationalError:
            continue
        offset += 100
        if not returned:
            break

    ## Sort reviews and render table
    reviews = sorted(reviews, key=attrgetter('score'), reverse=True)     
    table = ReviewTable(reviews)
    return render_template('yelp_table.html', table=table)

if __name__ == "__main__":
        app.run()
