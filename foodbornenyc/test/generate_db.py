"""
Generates a small test DB by recreating the tables and copying over a few entries.
"""
from sqlalchemy.orm.session import make_transient, make_transient_to_detached
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import text
from sqlalchemy import MetaData

import foodbornenyc.models.models as models
from foodbornenyc.models.businesses import Business, business_category_table
from foodbornenyc.models.documents import YelpReview, Document, documents
from foodbornenyc.models.locations import Location

from foodbornenyc.util.util import sec_to_hms, get_logger
logger = get_logger(__name__, level="INFO")

test_config = {
    'user': 'johnnybananas',
    'password': 'placeholder_password',
    'dbhost': 'toy.db',
    'dbbackend':'sqlite'
}

# do NOT call this before copy_tables() in the same session. you will get a
# mapper error. it seems like the Metadata object that controls table relations
# is persisted even across different engines, so dropping tables in the test db
# messes up calls to the regular db.
def reset_test_db():
    logger.info("Resetting all tables in %s", test_config['dbhost'])
    models.drop_all_tables(test_config)
    models.setup_db(test_config)


def copy_tables():
    toy = models.get_db_session(test_config)
    db = models.get_db_session()

    logger.info("Populating test tables")

    businesses = db.query(Business).order_by(Business.id)[0:5]
    locations = [b.location for b in businesses]
    # [b.categories ...] is a list of lists, so we need a little more processing
    categories = set().union(*[b.categories for b in businesses])

    reviews = []
    for b in businesses:
        reviews.extend(
            db.query(YelpReview).filter(YelpReview.business_id == b.id)[0:5]
        )
    documents = [r.document for r in reviews]
    doc_assoc = [r.document_rel for r in reviews]

    tables = [businesses, locations, categories, reviews, documents, doc_assoc]

    # detach all objects from db session before putting them in toy
    for t in tables:
        for obj in t: make_transient(obj)

    # only after *everything* is transient do we add anything
    for t in tables: toy.add_all(t)

    # in addition we add the junction table for business categories
    b_ids = [b.id for b in businesses]
    business_cat = db.execute(business_category_table.select().
            where(business_category_table.c.business_id.in_(
                [b.id for b in businesses]
            )))

    for row in business_cat:
        toy.execute(business_category_table.insert(), row)

    toy.commit()
