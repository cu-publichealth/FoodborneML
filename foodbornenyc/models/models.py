"""

The main module of the models package

To get the configured database engine, call:
    get_db_engine()

To get a session for the DB call:
    get_db_session()

To set up the database schema call:
    setup_db()

To drop all tables from the database call:
    drop_all_tables()

"""
import traceback

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from metadata import metadata
from foodbornenyc.db_settings import database_config as db_config

from foodbornenyc.util.util import get_logger
logger = get_logger(__name__)

def get_db_engine(config={}, echo=False, verbose=False):
    """Take the database settings and construct an engine for the database

    Args:
        config (dict of str: str): DB connection configuration; any blank setting
            defaults to db_settings.py settings
        echo (bool): If `True` SQLAlchemy will print all SQL statements to stdout
        verbose (bool): If `True` the logger will notify when the engine is created

    Returns:
        engine: The SQLAlchemy engine object.  Used to execute statements or create ORM sessions
    """
    c = db_config.copy()
    c.update(config)

    if 'sqlite' in (c['dbbackend']):
        engine = create_engine('%s:///%s' % (c['dbbackend'], c['dbhost']), echo=echo)
    else:
        engine = create_engine('%s://%s:%s@%s?charset=utf8'
                                % (c['dbbackend'], c['user'], c['password'], c['dbhost']), echo=echo)

    if verbose:
        logger.info("Engine created for %s::%s", db_host, user)

    return engine

def get_db_session(config={}, echo=False, autoflush=True, autocommit=False):
    """Create a SQLAlchemy `Session` bound to the engine defined in `get_db_engine`

    Args:
        echo (bool): Whether echo sql statements
        autoflush (bool): If `False` the session won't automatically flush
                          changes to the transaction. Use in conjuntion with
                          `autocommit=True`.
        autocommit (bool): If `True`, the transaction must be explicitly opened and closed.

    Returns:
        session (Session): A session object bound to the engine

    Notes:
        `autoflush` and `autocommit` should only be set to `False` and `True` if you want to
        manage transactions yourself. Useful if you have to deal with a large amount of data
        and want to piece transactions.

        To do this correctly, use a session begin context to make sure the xact is always commited.
        eg:

        ```
        db = get_db_session(autoflush=False, autocommit=True)
        with db.begin():
            # use the session here
            # you can't not commit using the `with` context
        ```
    """
    return sessionmaker(bind=get_db_engine(config=config, echo=echo),
                        autoflush=autoflush,
                        autocommit=autocommit)()

def setup_db(config={}):
    """Set up all tables in the database, or add tables that don't yet exist.

    Reflects all tables that have been registered with the `metadata` object in the `models` module.

    Args:
        None

    Returns:
        None
    """
    engine = get_db_engine(config, echo=True)
    #instantiate the schema
    try:
        metadata.create_all(engine)
        logger.info("Successfully instantiated Database with model schema")
    except Exception:
        logger.error("Failed to instantieate Database with model schema")
        traceback.print_exc()

def drop_all_tables(config={}):
    """Tear down all data, tables, and the schema.  Very dangerous.

    Args:
        None

    Returns:
        None
    """
    engine = get_db_engine(config, echo=True)
    try:
        metadata.reflect(engine, extend_existing=True)
        metadata.drop_all(engine)
        logger.info("Successfully dropped all the database tables in the schema")
    except Exception:
        logger.error("Failed to drop all tables")
        traceback.print_exc()
