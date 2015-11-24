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
from sqlalchemy import MetaData
metadata = MetaData()
import locations
import documents
import businesses

def getDBEngine(echo=False):
    from sqlalchemy import create_engine

    user = 'user'
    password = 'password'
    # db_host = '192.168.56.101:1433/dohmh2'
    # db_host = 'db-pc03.cs.columbia.edu:1433/dohmh'
    db_host = '128.59.22.184:1433/dohmh'
    engine = create_engine('mssql+pymssql://%s:%s@%s?charset=utf8'\
        % (user, password, db_host), echo=echo )

    # POSTGRES
    # db_host = '128.59.22.184:5432/dohmh'
    # engine = create_engine('postgresql+psycopg2://%s:%s@%s'\
    #     % (user, password, db_host), echo=echo )

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
    engine = getDBEngine(echo=True)
    # drop the schema
    try:
        metadata.reflect(engine, extend_existing=True)
        metadata.drop_all(engine)
        logger.info("Successfully dropped all the database tables in the schema")
    except:
        logger.error("Failed to drop all tables")
        traceback.print_exc()


