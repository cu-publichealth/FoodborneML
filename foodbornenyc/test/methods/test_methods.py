from foodbornenyc.methods.yelp_classify import YelpClassify

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

	#verify that entries are filled

	#verify that entries are at least reasonable?

if __name__ == '__main__':
	classify_reviews()
