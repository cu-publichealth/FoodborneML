"""
Generates a small test DB by recreating the tables and copying over a few entries.
"""
from sqlalchemy.orm.session import make_transient

import foodbornenyc.models.models as models
from foodbornenyc.models.businesses import Business
from foodbornenyc.models.locations import Location

from foodbornenyc.util.util import sec_to_hms, get_logger
logger = get_logger(__name__, level="INFO")

test_config = {
    'user': 'johnnybananas',
    'password': 'placeholder_password',
    'dbhost': 'toy.db',
    'dbbackend':'sqlite'
}

def recreate_test_db():
    reset_test_db()
    copy_tables()

def reset_test_db():
    logger.info("Resetting all tables in %s", test_config['dbhost'])
    models.drop_all_tables(test_config)
    models.setup_db(test_config)


def copy_tables():
    toy = models.get_db_session(test_config)
    db = models.get_db_session()
    logger.info("Populating test tables")
    businesses =  db.query(Business).order_by(Business.id)[0:5]
    locations = []
    for business in businesses:
        business.location_address # force-load location
        locations.append(business.location)

    # detach objects from db session before putting them in toy
    for b in businesses: make_transient(b)
    for l in locations: make_transient(l)

    toy.add_all(businesses)
    toy.add_all(locations)
    toy.commit()

def read_tables():
    toy = models.get_db_session(test_config)
    for b in toy.query(Business):
        print(b)
        print(b.location)
