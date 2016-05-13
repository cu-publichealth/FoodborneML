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
from foodbornenyc.UI.dashboard import get_yelp_score_distribution
from foodbornenyc.UI.investigations import get_sick_business_dict


from flask import Flask
from flask import render_template
from flask.ext.navigation import Navigation
from flask import request

all_sick_businesses = {}

app = Flask(__name__)


##Dashboard
@app.route("/")
def hello():
        return render_template('dashboard.html')

@app.route('/dashboard/')
def dashboard():
	return render_template('dashboard.html')
    ##return get_yelp_score_distribution();

# Yelp Reviews
@app.route('/yelp/')
@app.route('/yelp', methods=['GET'])
def yelp():
    search_params = make_param_tuple(request.args.get('thr'), request.args.get('order_by'),
                                     request.args.get('num_results'), request.args.get('page'),
                                     request.args.get('start_date'), request.args.get('end_date'),
                                     100)

    yelp_reviews = get_yelp_sick_reviews(echo=False, search_params=search_params)
    ## Render template
    return render_template('review_table.html', reviewtype="Yelp", reviews=yelp_reviews,
                            get_review_file=get_review_file, searchtype="yelp", 
                            searchparams=search_params)

# Tweets
@app.route('/twitter/')
@app.route('/twitter', methods=['GET'])
def twitter():
    search_params = make_param_tuple(request.args.get('thr'), request.args.get('order_by'),
                                 request.args.get('num_results'), request.args.get('page'),
                                 request.args.get('start_date'), request.args.get('end_date'),
                                 100)
    tweets = get_twitter_sick_reviews(echo=False, search_params=search_params)
    return render_template('review_table.html', reviewtype="Twitter", reviews=tweets,
                            get_review_file=get_review_file, searchtype="twitter",
                            searchparams=search_params)

#Outbreaks
@app.route('/investigations/')
def investigations():
    search_params = make_param_tuple(request.args.get('thr'), request.args.get('order_by'),
                                     request.args.get('num_results'), request.args.get('page'),
                                     request.args.get('start_date'), request.args.get('end_date'),
                                     -1)
    all_sick_businesses = get_sick_business_dict(search_params=search_params)
    return render_template('investigations.html', businesses=all_sick_businesses,
                            get_review_file=get_review_file, searchparams=search_params)


# Helpfer function for which review html code to use
def get_review_file(reviewtype):
    template = "";
    if (reviewtype == "Yelp"):
        template = "/yelp_review.html"
    elif reviewtype == "Twitter":
        template = "/twitter_review.html"
    return template

## Helper method of yelp params
def make_param_tuple(thr, sortby, num_results, page, start, end, default_num_results):
    if thr == None:
        thr = 5 ## threshold is in tenths bc of how it's displayed on search bar
    thr = int(thr)

    if sortby == None:
        sortby='severity'

    if (num_results == None):
        num_results = default_num_results
    num_results = int(num_results)

    if (page == None):
        page = 1
    page = int(page)

    if (start == None):
        start = ""

    if (end == None):
        end = ""

    return (thr, sortby, num_results, page, start, end)

if __name__ == "__main__":
        app.run()
