"""
Generates a small test DB by recreating the tables and copying over a few entries.
"""
import foodbornenyc.models.models as models

from foodbornenyc.models.businesses import Business, businesses
from foodbornenyc.models.locations import Location

from foodbornenyc.util.util import sec_to_hms, get_logger
logger = get_logger(__name__, level="INFO")

test_config = {
    'user': 'johnnybananas',
    'password': 'placeholder_password',
    'dbhost': 'toy.db',
    'dbbackend':'sqlite'
}

def make_test_db():
    # reset test db
    logger.info("Resetting test tables")
    models.drop_all_tables(test_config)
    models.setup_db(test_config)

    test_db = models.get_db_session(test_config)
    db = models.get_db_session()

    logger.info("Populating test tables")
    businesslist = []
    locationlist = []
    for b in db.query(Business).order_by(Business.id)[0:5]:
        businesslist.append(b.__dict__)

    test_db.execute(businesses.insert(), businesslist)
    test_db.commit()
    
