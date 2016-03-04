from foodbornenyc.methods.yelp_classify import *
from foodbornenyc.test.generate_test_db import *

# import foodbornenyc.models.models as models
# from foodbornenyc.models.businesses import Business, business_category_table
# from foodbornenyc.models.documents import YelpReview, Tweet, Document
# from foodbornenyc.models.locations import Location
# from foodbornenyc.models.metadata import metadata

from foodbornenyc.util.util import sec_to_hms, get_logger
logger = get_logger(__name__, level="WARNING")

def teardowm():
	# removes classification info
	pass

def classify_reviews():
	#classify reviews
	yc = YelpClassify()
	yc.classify_reviews(every=True, verbose=1)

def test_reasonable_proba():
	#verify that fp_pred are at least reasonable, based on test data
	#if any of them are over 0.5, print text
	db = models.get_db_session()
	query = db.query(Document.id, YelpReview.text, Document.__fp_pred) \
		.filter(Document.assoc_id == YelpReview.doc_assoc_id)[:]
	for doc in query:
		assert doc[2] >= 0
		assert doc[2] <= 1
		if doc[2] >= 0.5:
			#do some NLP here for quick validation?
			print "-----------SICK REVIEW FOUND------------"
			print "Document ID: " + str(doc[0])
			print "Probability: " + str(doc[2])
			print "Review text: " + str(doc[1])


def test_classify_time():
	#verify that the whole operation doesn't take too long, i.e. .3 seconds
	import time, datetime
	db = models.get_db_session()
	query = db.query(Document)[:]
	#takes difference of earliest and latest timestamps
	start = min([float(doc.fp_pred_time.strftime("%s.%f")) for doc in query])
	end = 	max([float(doc.fp_pred_time.strftime("%s.%f")) for doc in query])
	#print end - start
	assert end - start <= .3


if __name__ == '__main__':
	classify_reviews()
	test_reasonable_proba()
	test_classify_time()
