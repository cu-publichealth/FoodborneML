"""
YelpClassify

This method takes in Yelp reviews and classifies them.
Then persists those classifications to the corresponding doc model
"""
import datetime
from time import time

from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sklearn.externals import joblib


from foodbornenyc.settings import yelp_classify_config as config

from foodbornenyc.models.models import get_db_session
from foodbornenyc.models.documents import YelpReview, documents

from foodbornenyc.util.util import get_logger, sec_to_hms
logger = get_logger(__name__)

class YelpClassify(object):
    """Method to classify yelp reviews already loaded into the database"""
    def __init__(self, sick_path=None):
        """ Initialize the method object and it's classifier

        Args:
            sick_path (str): if specified, load the classifier from this path
                             else load from config

        Returns:
            None

        """
        if sick_path:
            self.sick = joblib.load(sick_path)
        else:
            self.sick = joblib.load(config['model_file'])

    def score_review(self, review):
        """ Take a YelpReview object and use `sick` to get the class probability,
            then set the sick_pred to the value in the review's document."""
        review.document.fp_pred = self.sick.predict_proba([review.text])[0][1]
        return review

    #TODO: Classifying reviews this way happens quite slowly. We should consider also adding this
    # functionality to `yelp_fast` so we don't need so manny transactions.
    # or we should at least try to optimize this strategy (possibly both)
    def classify_reviews(self, every=False, unseen=False, since=30, yield_per=1000, verbose=0):
        """Classify some set of `YelpReview`s' `Docuement` in the database

        Args:
            every (bool): Whether to just do them all.
                          Trumps other flags. Likely to __very__ slow.
            unseen (bool): If not `every`, classify all that don't yet have predictions.
                           Trumps `since`.
            since (int): Number of past days to classify reviews.
            yield_per (int): Will work with database in batches of that size.
            verbose (int): Degree of verbosity v.
                           - v = 0 Only specify number of reviews being classified
                           - v >= 1 Log when eaches review has been classified
                           - v >= 2 Echo SQL statements

        Returns:
            None

        """
        echo = True if verbose >= 2 else False
        db = get_db_session(echo=echo, autoflush=False, autocommit=True)
        with db.begin():
            if every:
                logger.info("Classifying all reviews. This could take a very long time")
                query = db.query(YelpReview).order_by(YelpReview.id.asc())
                count = db.query(func.count(YelpReview.id)).scalar()
            elif unseen:
                logger.info("Classifying all unclassified reviews")
                # this requires running some special core level queries because of the dynamic document association
                # this way is actually faster anyways
                unseen_q = select([documents.c.id]).where(documents.c.fp_pred.is_(None))
                query = (db.query(YelpReview)
                           .filter(YelpReview.id.in_(unseen_q))
                           .order_by(YelpReview.id.asc()))
                count = (db.execute(
                           select([func.count(documents.c.id)])
                           .where(documents.c.fp_pred.is_(None)))
                           .scalar()) # instead of tuple
            else:
                logger.info("Classifying all reviews from the past %i days", since)
                backdate = datetime.datetime.now() - datetime.timedelta(since)
                query = (db.query(YelpReview)
                           .filter(YelpReview.created >= backdate)
                           .order_by(YelpReview.created.desc()))
                count = (db.query(func.count(YelpReview.created))
                           .filter(YelpReview.created >= backdate)
                           .scalar()) # instead of tuple

        logger.info("Classifying %i total reviews", count)
        start = time()
        offset = 0
        while True:
            returned = False
            try:
                with db.begin():
                    for i, review in enumerate(query.limit(yield_per).offset(offset)):
                        returned = True
                        if verbose:
                            logger.info("Classified Review #%i/%i", offset+i+1, count)
                        self.score_review(review)
                    logger.info("Commiting Predictions")
            except OperationalError:
                continue # if commit error, try again with same offeset
            offset += yield_per
            if not returned:
                break
        logger.info("Classified %i reviews in %i:%i:%i (h:m:s)", count, sec_to_hms(time()-start))

    
