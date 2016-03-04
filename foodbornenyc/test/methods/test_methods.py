from foodbornenyc.methods.yelp_classify import YelpClassify
from foodbornenyc.db_settings import database_config as config

from foodbornenyc.util.util import sec_to_hms, get_logger
logger = get_logger(__name__, level="WARNING")

def test_classify_reviews():
    #classify reviews
    yc = YelpClassify()
    yc.classify_reviews(every=True, verbose=1)

    #verify that entries are filled

    #verify that entries are at least reasonable?

if __name__ == '__main__':
    test_classify_reviews()
