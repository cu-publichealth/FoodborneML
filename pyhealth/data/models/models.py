"""

The main module of the models package

To get the configured database engine, call:
    getDBEngine()

To get a session for the DB call:
    getDBSession()

To set up the database schema call:
    setupDB()

"""
import traceback

from ...util.util import getLogger
logger = getLogger(__name__)


def getDBEngine(echo=False):
    from sqlalchemy import create_engine

    user = 'user'
    password = 'password'
    db_host = '192.168.56.101:1433/dohmh2'

    engine = create_engine('mssql+pymssql://%s:%s@%s?charset=utf8'\
        % (user, password, db_host), echo=echo )

    logger.info("Engine created for %s::%s" % (db_host, user))

    return engine

def getDBSession(echo=False):
    from sqlalchemy.orm import sessionmaker
    return sessionmaker(bind=getDBEngine(echo=echo))



def setupDB():
    engine = getDBEngine(echo=True)
    from base import Base
    #instantiate the schema
    try:
        Base.metadata.create_all(engine)
        logger.info("Successfully instantiated Database with model schema")
    except:
        logger.error("Failed to instantieate Database with model schema")
        traceback.print_exc()



