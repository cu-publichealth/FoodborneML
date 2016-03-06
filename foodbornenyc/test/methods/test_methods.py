from foodbornenyc.methods.yelp_classify import *
from foodbornenyc.test.generate_test_db import *

import pytest

#BUG/ISSUE: pytest doesn't support specifying logging output

from foodbornenyc.util.util import sec_to_hms, get_logger
logger = get_logger(__name__, level="WARNING")

db = models.get_db_session()

@pytest.fixture(scope='module')
def classify(request):
	""" Classify reviews and return YelpClassify() """

	logger.info("SETUP")
	yc = YelpClassify()
	yc.classify_reviews(every=True, verbose=1)

	#create copy of yelp_reviews
	#only necessary to restore yelp_reviews.text and yelp_reviews.updated_at based on the tests we currently have
	_oldquery = db.query(YelpReview).order_by(YelpReview.id)
	oldquery = [ {
		'text': yr.text,
		'updated_at': yr.updated_at
		} for yr in _oldquery]

	#unclassify, i.e. remove fp_pred and fp_pred_time, and restore yelp_reviews
	def teardown():
		logger.info("TEARING DOWN")
		newquery = db.query(YelpReview).order_by(YelpReview.id)
		for old, new in zip(oldquery, newquery):
			new.text = old['text']
			new.updated_at = old['updated_at']
			new.document.fp_pred = None
			new.document.fp_pred_time = None

		db.commit()

	request.addfinalizer(teardown)

	return yc

def test_reasonable_proba(classify):
	""" Verify that fp_pred are at least reasonable, based on test data """

	query = db.query(Document.id, YelpReview.text, Document.__fp_pred) \
		.filter(Document.assoc_id == YelpReview.doc_assoc_id)
	for doc in query:
		assert doc[2] >= 0
		assert doc[2] <= 1
		#if any of them are over 0.5, log text
		if doc[2] >= 0.5:
			#do some NLP here for quick validation?
			logger.debug("SICK REVIEW FOUND")
			logger.debug("Document ID: " + str(doc[0]))
			logger.debug("Probability: " + str(doc[2]))
			logger.debug("Review text: " + str(doc[1]))


def test_classify_time(classify):
	""" Verify that the whole operation doesn't take too long, i.e. .2 seconds """

	import time, datetime
	query = db.query(Document)

	#takes difference of earliest and latest timestamps
	start = min([float(doc.fp_pred_time.strftime("%s.%f")) for doc in query])
	end = 	max([float(doc.fp_pred_time.strftime("%s.%f")) for doc in query])
	assert end - start <= .2

def test_obvious_triggers(classify):
	""" Verify that adding some obvious trigger text would cause probabilities to jump """

	trigger_text = [u"later that day I threw up.", u"i felt really sick the morning after.", u"two of my friends also got sick."]
	query = db.query(YelpReview).order_by(YelpReview.id)

	#keep old data
	temp_text = []
	temp_proba = []
	temp_pred_time = []

	for review in query:
		temp_text.append(review.text)
		temp_proba.append(review.document.fp_pred)
		temp_pred_time.append(review.document.fp_pred_time)

		#modify text to include trigger text
		review.text += u' '.join(trigger_text)
	db.commit()

	#classify again
	classify.classify_reviews(every=True, verbose=1)

	for review, proba in zip(query, temp_proba):
		assert review.document.fp_pred >= 0.48
		assert review.document.fp_pred - proba >= 0.11

	assert sum([review.document.fp_pred - proba for review, proba in zip(query, temp_proba)])/len(temp_proba) >= 0.20

	#restore
	for review, text, proba, time in zip(query, temp_text, temp_proba, temp_pred_time):
		review.text = text
		review.document.fp_pred = proba
		review.document.fp_pred_time = time

	db.commit()

