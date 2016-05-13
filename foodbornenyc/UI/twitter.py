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


# Query database for all reviews matching search params
# Return list of UITwitterReview objects
def get_twitter_sick_reviews(echo, search_params):
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


    db = get_db_session(echo=echo, autoflush=False, autocommit=True)
    count = 0
    ## Construct query to get all positive reviews
    with db.begin():
        all_tweets = select([documents.c.id])
        query = (db.query(Tweet).filter(Tweet.id.in_(all_tweets)).order_by(Tweet.id.asc()))

    offset = num_results * (page - 1)
    tweets = []
    ## Collect all reviews meeting query criteria
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
                            
                            ## The DB doesn't yet have functionality for Twitter reviews to be
                            ## linked to businesses, but once that happens we should adapt this.
                            business = UIBusiness("Unknown business", "XXX", "XXX", "X", "twitter.com",
                                              "twitter.com")
                            tweets.append(UITwitterReview(business, review.text, review.document.fp_pred,
                                      review.document.created, "Twitter", review.user_id, review.id))
        except OperationalError:
            break

        if is_limit or (not returned):
            break
        # Otherwise, continue until there are no more reviews
        offset += 100 ## when no limit, loop on sets of 100

    ## Sort reviews
    if (sortby == "severity"):
        tweets = sorted(tweets, key=attrgetter('score'), reverse=True)
    else:
        tweets = sorted(tweets, key=attrgetter('created'))

    return tweets
