from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sklearn.externals import joblib
from foodbornenyc.settings import yelp_classify_config as config
from operator import attrgetter
from foodbornenyc.models.models import get_db_session
from foodbornenyc.models.documents import YelpReview, documents
from foodbornenyc.models.businesses import Business, businesses

from foodbornenyc.util.util import get_logger, sec_to_hms


from flask import Flask
from flask import render_template
from flask_table import Table, Col


## Buckets from 0-.1, .1-.2, .2-.3, etc (inclusive of lower bound, exclusive of upper bound)
def get_yelp_score_distribution():
    db = get_db_session(echo=echo, autoflush=False, autocommit=True)
    counts = []
    i = 0
    while i <= 1:
        bucket_count = (db.execute(select([func.count(documents.c.id)]).where(
            and_(
                documents.c.fp_pred >= i,
                documents.c.fp_pred < i + 0.1
                )
            )).scalar())
        i += .1
        counts.append(bucket_count)
    return counts
