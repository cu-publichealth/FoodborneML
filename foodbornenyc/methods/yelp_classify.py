"""
YelpClassify

This method takes in Yelp reviews and classifies them.  Then persists those classifications to the corresponding doc model
"""
# import importlib #lets you import modules introspectively
from ..settings import yelp_classify_config as config

from ..models.models import getDBSession, page_query
from ..models.documents import YelpReview, documents

from ..util.util import getLogger
logger = getLogger(__name__)

from sqlalchemy import func, select
from sqlalchemy.orm import load_only
from sklearn.externals import joblib
import datetime
from time import time

class YelpClassify(object):

    def __init__(self, sick_path=None):
        # currently assumes module name and pipeline name are the same
        # pipe_module = importlib.import_module("..pipelines.%s" % (pipeline_name))
        # self.pipeline = pipe_module.pipeline
        if sick_path:
            self.sick = joblib.load(sick_path)
        else:
            self.sick = joblib.load(config['model_file'])

    def score_review(self, review):
        """ Take a YelpReview object and use `sick` to get the class probability
            , then set the sick_pred to the value in the review's document."""
        review.document.fp_pred = self.sick.predict_proba([review.text])[0][1]
        return review

    def classify_reviews(self, all=False, any=False, since=30, yield_per=1000, verbose=0):
        echo = True if verbose >= 2 else False
        db = getDBSession(echo=echo, autoflush=False, autocommit=True)
        with db.begin():
            if all:
                logger.info("Classifying all reviews. This could take a very long time")
                query = db.query(YelpReview).order_by(YelpReview.id.asc())
                count = db.query(func.count(YelpReview.id)).scalar()
            elif any:
                logger.info("Classifying all unclassified reviews")
                # this requires running some special core level queries because of the dynamic document association
                # this way is actually faster anyways
                unseen_q = select([documents.c.id]).where(documents.c.fp_pred.is_(None))
                query = db.query(YelpReview).filter(YelpReview.id.in_(unseen_q)).order_by(YelpReview.id.asc())
                count = db.execute(select([func.count(documents.c.id)]).where(documents.c.fp_pred.is_(None))).scalar()
            else:
                logger.info("Classifying all reviews from the past %i days" % since)
                delta = datetime.timedelta(since)
                backdate = datetime.datetime.now() - delta
                query = (db.query(YelpReview).filter(YelpReview.created >= backdate)
                                            .order_by(YelpReview.created.desc()))
                count = (db.query(func.count(YelpReview.created))
                                            .filter(YelpReview.created >= backdate)
                                            # .order_by(YelpReview.created.desc())
                                            .scalar())

        logger.info("Classifying %i total reviews" % count)
        offset = 0
        while True:
            returned = False
            with db.begin():
                for i, review in enumerate(query.limit(yield_per).offset(offset)):
                    returned = True
                    if verbose:
                        logger.info("Classified Review #%i" % (offset+i))
                    self.score_review(review)
                offset += yield_per
                logger.info("Commiting Predictions")
            if not returned:
                break
        # for i, review in enumerate(query):#page_query(query, yield_per)):
        #     if verbose:
        #         logger.info("Classified Review #%i" % i)
        #     self.score_review(review)
        #     if i and (i % yield_per == 0):
                
        #         db.flush()

        # # TODO: Make it not all one giant transaction, but page throught the commits
        # db.commit()


    
