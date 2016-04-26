"""
An integration test suite that verifies the sanity of the Yelp Classifier model
output and corresponding database method on a small sample of real Yelp reviews.
"""

from foodbornenyc.methods.yelp_classify import *
from foodbornenyc.test.test_db import *
import foodbornenyc.test.test_db as t

from mock import Mock, patch
import pytest, os

#BUG/ISSUE: pytest doesn't support specifying logging output

from foodbornenyc.util.util import sec_to_hms, get_logger, xuni, xstr
logger = get_logger(__name__, level="INFO")

db = get_db_session()

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

@pytest.fixture(scope='module')
@patch('foodbornenyc.methods.yelp_classify.get_db_session')
def classify(db_session, request):
    """ Classify reviews and return YelpClassify() """

    logger.info("SETUP")
    # setup test database mock
    db_session.side_effect = get_db_session

    # populate database
    clear_tables()
    for line in open(os.path.join(__location__, "populate.sql"), "r"):
        db.execute(xuni(line))
    db.commit()

    yc = YelpClassify()
    yc.classify_reviews(every=True, verbose=1)

    return yc

def test_reasonable_proba(classify):
    """ Verify that fp_pred are at least reasonable, based on test data """

    query = db.query(YelpReview)
    for review in query:
        doc = review.document
        assert doc.__fp_pred >= 0
        assert doc.__fp_pred <= 1
        #if any of them are over 0.5, log text
        if doc.__fp_pred >= 0.5:
            #do some NLP here for quick validation?
            logger.debug("SICK REVIEW FOUND")
            logger.debug("Document ID: " + str(doc.id))
            logger.debug("Probability: " + str(doc.__fp_pred))
            logger.debug("Review text: " + str(review.text))


def test_classify_time(classify):
    """ Verify that the whole operation doesn't take too long, ie .2 seconds """

    import time, datetime
    query = db.query(Document)

    #takes difference of earliest and latest timestamps
    start = min([float(doc.fp_pred_time.strftime("%s.%f")) for doc in query])
    end =     max([float(doc.fp_pred_time.strftime("%s.%f")) for doc in query])
    assert end - start <= 2

# @patch('foodbornenyc.methods.yelp_classify.get_db_session')
# def test_obvious_triggers(db_session, classify):
#     """ Verify that adding obvious trigger text causes probabilities to jump """

#     trigger_text = [u"later that day I threw up.",
#                     u"i felt really sick the morning after.",
#                     u"two of my friends also got sick."]
#     query = db.query(YelpReview).order_by(YelpReview.id)
#     db_session.side_effect = get_db_session

#     #keep old data
#     temp_text = []
#     temp_proba = []
#     temp_pred_time = []

#     for review in query:
#         temp_text.append(review.text)
#         temp_proba.append(review.document.fp_pred)
#         temp_pred_time.append(review.document.fp_pred_time)

#         #modify text to include trigger text
#         review.text += u' '.join(trigger_text)
#     db.commit()

#     #classify again
#     classify.classify_reviews(every=True, verbose=1)

#     for review, proba in zip(query, temp_proba):
#         assert review.document.fp_pred >= 0.45
#         assert review.document.fp_pred - proba >= 0.11

#     # average of jump in probability after adding trigger text should be high
#     proba_diff = [rev.document.fp_pred - p for rev, p in zip(query, temp_proba)]
#     assert sum(proba_diff)/len(proba_diff) >= 0.20
