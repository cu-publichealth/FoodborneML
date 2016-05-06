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


def get_sick_business_dict():
	yelp_reviews = get_yelp_sick_reviews(echo=False)
	# tweets = get_twitter_sick_reviews(echo=False)

	businesses = {}

	for review in yelp_reviews:
		## If Business in dict
		if (review.business.id in businesses):
			businesses[review.business.id].append(review)
		## IF business not in dict
		else:
			businesses[review.business.id] = [review]

	# for review in tweets:
	# 	## Business in dict already
	# 	if (review.business.id in businesses):
	# 		businesses[review.business.id].append(review)
	# 	## Business not in dict
	# 	else:
	# 		businesses[review.business.id] = [review]


	business_tuples = []

	## convert to list of tuples so that businesses can be sorted by
	## number and severity of reviews

	##tuple format: (businessid, reviews_list)
	for business in businesses:
		business_tuples.append((businesses[business][0].business, businesses[business]))
	print business_tuples[0]

	business_tuples.sort(key=lambda t: len(t[1]), reverse=True)
	print business_tuples[0]
	return business_tuples
