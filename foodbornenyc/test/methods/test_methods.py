from foodbornenyc.methods.yelp_classify import YelpClassify
from foodbornenyc.db_settings import database_test_config as config

from foodbornenyc.util.util import sec_to_hms, get_logger
logger = get_logger(__name__, level="INFO")

def classify_reviews():
    yc = YelpClassify()
    yc.classify_reviews(dbconfig=config, every=True, verbose=3)


if __name__ == '__main__':
    classify_reviews()
