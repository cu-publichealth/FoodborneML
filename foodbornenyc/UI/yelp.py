from datetime import datetime as dt
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


# Query database for yelp reviews matching search params
# Returns list of UIYelpReview Objects
# Searches for reviews at or above given threshold, within date range if given
# Sorts by severity or date, defaults to severity
# Limited to num_results, -1 for no limit
def get_yelp_sick_reviews(echo, search_params):

    (threshold, sortby, num_results, page, start_date, end_date) = search_params
    threshold = (1.0 / 10) * threshold ## convert to tenths

    # Reformat date params for comparison later
    if len(start_date) > 0:
        start_date = dt.strptime(start_date, "%Y-%m-%d")
    else:
        start_date = None
    if len(end_date) > 0:
        end_date = dt.strptime(end_date, "%Y-%m-%d")
    else:
        end_date = None

    ## Record whether a limit was given
    is_limit = (num_results != -1)

    # If no limit, set num_results to 100 for querying in a loop
    if not is_limit:
        num_results = 100 

    # Setup query using parameters
    db = get_db_session(echo=echo, autoflush=False, autocommit=True)
    count = 0
    ## Construct query to get all positive reviews
    with db.begin():
        high_scores = high_scores = select([documents.c.id]).where(documents.c.fp_pred > threshold)
        query = (db.query(YelpReview).filter(YelpReview.id.in_(high_scores)).order_by(
            documents.c.fp_pred))

    ## Collect all reviews meeting query criteria
    ## -- if no num_results was given, loop repeats for all reviews
    offset = num_results * (page - 1)
    reviews = []
    while True:
        returned = False
        try:
            with db.begin():
                for i, review in enumerate(query.limit(num_results).offset(offset)):
                    returned = True

                    ## only proceed if review's date follows start_date, if applicable
                    if (start_date == None or (review.document.created >= start_date)):
                        ## only proceed if review's date preceeds end_date, if applicable
                        if (end_date == None or (review.document.created <= end_date)):
                            
                            # Get business info
                            business_query = db.query(Business).filter(Business.id.in_(
                                    select([businesses.c.id]).where( businesses.c.id ==
                                           review.business_id)))

                            # Create UIBusiness object and append UIYelpReview object to reviews
                            # list. Only retieves one business for the review.
                            for j, business in enumerate(business_query.limit(1).offset(0)):
                                business = UIBusiness(business.id, business.name, business.phone,
                                                      business.rating, business.url,
                                                      business.business_url)
                                reviews.append(UIYelpReview(business, review.text,
                                                            "%.3f" % review.document.fp_pred,
                                                            review.document.created, "Yelp",
                                                            review.user_name, review.id))
        except OperationalError:
            break

        # If limit was given, or no results were found, break
        if is_limit or (not returned):
            break

        # Otherwise, continue until there are no more reviews
        offset += 100 ## when no limit, loop on sets of 100


    ## Sort reviews
    if (sortby == "severity"):
        reviews = sorted(reviews, key=attrgetter('score'), reverse=True)
    else:
        reviews = sorted(reviews, key=attrgetter('created'))


    ##return ReviewTable(reviews)
    return reviews
