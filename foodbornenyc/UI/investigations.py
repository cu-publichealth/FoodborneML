from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sklearn.externals import joblib
from foodbornenyc.settings import yelp_classify_config as config
from operator import attrgetter
from foodbornenyc.models.models import get_db_session
from foodbornenyc.models.documents import YelpReview, documents
from foodbornenyc.models.businesses import Business, businesses

from foodbornenyc.util.util import get_logger, sec_to_hms

from foodbornenyc.UI.reviewclasses import Review, UIYelpReview, UITwitterReview, UIBusiness
from foodbornenyc.UI.yelp import get_yelp_sick_reviews
from foodbornenyc.UI.twitter import get_twitter_sick_reviews


from flask import Flask
from flask import render_template
from flask.ext.navigation import Navigation
from flask import request

def get_sick_business_dict(search_params):
	# Get all reviews with default settings -- 0.5 threshold, no limit
	yelp_reviews = get_yelp_sick_reviews(echo=False, search_params=search_params)
	# tweets = get_twitter_sick_reviews(echo=False, search_params=DEFAULT_SEARCH_PARAMS)

	# Now iterate through yelp reviews and add to dict of reviews indexed by business id
	business_reviews = {}
	for review in yelp_reviews:
		## If Business in dict
		if (review.business.id in business_reviews):
			business_reviews[review.business.id].append(review)
		## IF business not in dict
		else:
			business_reviews[review.business.id] = [review]

	# Tweets do not yet have support for businesses in db, so until then we can't use this
	# for review in tweets:
	# 	## Business in dict already
	# 	if (review.business.id in business_reviews):
	# 		business_reviews[review.business.id].append(review)
	# 	## Business not in dict
	# 	else:
	# 		business_reviews[review.business.id] = [review]


	## convert to list of tuples so that businesses can be sorted by
	## number of reviews
	business_tuples = []
	for business in business_reviews:
		avg_score  = 0
		for review in business_reviews[business]:
			avg_score += float(review.score)
		avg_score = (1.0 * avg_score) / len(business_reviews[business])

		##tuple format: (businessid, reviews_list, num_reviews, avg score)
		business_tuples.append((business_reviews[business][0].business,
								business_reviews[business],
								len(business_reviews[business]),
								avg_score))

	# Sort businesses by number of reviews
	business_tuples.sort(key=lambda t: t[2], reverse=True)
	return business_tuples
