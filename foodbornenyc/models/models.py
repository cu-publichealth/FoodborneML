"""

The main module of the models package

To get the configured database engine, call:
    getDBEngine()

To get a session for the DB call:
    getDBSession()

To set up the database schema call:
    setupDB()

To drop all tables from the database call:
    dropAllTables()

"""
import traceback

from ..util.util import getLogger
logger = getLogger(__name__)

# metadata object shared between models
from sqlalchemy import MetaData, func
metadata = MetaData()
# import each of the used model definition files
import locations
import businesses
import documents
import download_history

from ..settings import database_config as config

def getDBEngine(echo=False, verbose=False):
    from sqlalchemy import create_engine

    user = config['user']
    password = config['password']
    db_host = config['dbhost']

    engine = create_engine('mssql+pymssql://%s:%s@%s?charset=utf8'\
        % (user, password, db_host), echo=echo )

    if verbose:
        logger.info("Engine created for %s::%s" % (db_host, user))

    return engine

def getDBSession(echo=False, autoflush=True, autocommit=False):
    from sqlalchemy.orm import sessionmaker
    return sessionmaker(bind=getDBEngine(echo=echo), 
                        autoflush=autoflush,
                        autocommit=autocommit)()

def setupDB():
    engine = getDBEngine(echo=True)
    #instantiate the schema
    try:
        metadata.create_all(engine)
        logger.info("Successfully instantiated Database with model schema")
    except:
        logger.error("Failed to instantieate Database with model schema")
        traceback.print_exc()

def dropAllTables():
    print "BLAH"
    engine = getDBEngine(echo=True)
    # drop the schema
    try:
        metadata.reflect(engine, extend_existing=True)
        metadata.drop_all(engine)
        logger.info("Successfully dropped all the database tables in the schema")
    except:
        logger.error("Failed to drop all tables")
        traceback.print_exc()

def page_query(query, yield_per):
    """Do the same thing as yield_per with eager loading.
    Inspired by http://stackoverflow.com/questions/1145905/sqlalchemy-scan-huge-tables-using-orm"""
    offset = 0
    while True:
        returned = False
        for elem in query.limit(yield_per).offset(offset):
            returned = True
            yield elem
        offset += yield_per
        if not returned:
            break
