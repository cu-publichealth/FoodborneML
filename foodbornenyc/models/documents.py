"""
Contains document models:

1. Document  (a polymorphic associative table)
2. YelpReview
3. Tweet

This inheritance pattern is closely modeled from Source: http://techspot.zzzeek.org/2007/05/29/polymorphic-associations-with-sqlalchemy/

Document is a polymorphic parent of specific document types.  It contains all of things we care about at document level, like labels and predictions

The children instantiate specific instances of document types, like YelpReview or Tweet

Generally avoid messing with the `document_associations` table, the `DocumentAssoc` class, and the `documentable` function

When creating a new type of document, just create the class, table, and mapper as usual, 
but then add `documentable(DocSubClass, 'document')`
and the appropriate association with correct integrity constraints will be created. Minimal extra code.

For example:
    ```
    db = getDBSession()
    yr = db.query(YelpReview).first()

    print yr.document


"""
from datetime import datetime

from sqlalchemy import Column, Table
from sqlalchemy import Integer, Float, String, UnicodeText, DateTime, Boolean
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint, ForeignKey
from sqlalchemy import and_
from sqlalchemy.orm import mapper, relationship, backref, relation, class_mapper

from ..util.util import getLogger
logger = getLogger(__name__)

from models import metadata

class DocumentAssoc(object):
    def __init__(self, id, name):
        self.assoc_id=id
        self.type=name

document_associations = Table('document_associations', metadata,
    Column('assoc_id', String(64), primary_key=True),
    Column('type', String(50), nullable=False)
)


def documentable(cls, name):
    """documentable 'interface'."""
    mapper = class_mapper(cls)
    table = mapper.local_table
    mapper.add_property('document_rel', relation(DocumentAssoc, backref=backref('_backref_%s' % table.name, uselist=False)))

    # scalar based property decorator
    def get(self):
        return self.document_rel.document[0]
    def set(self, value):
        if self.document_rel is None:
            self.document_rel = DocumentAssoc(self.id, table.name)
        self.document_rel.document = [value]
    setattr(cls, name, property(get, set))

class Document(object):
    """ TODO: Fill in the docstring for Document class """
    source = property(lambda self: getattr(self.association, '_backref_%s' % self.association.type))

    def __init__(self, id):#, id=id, type=type):
        self.id = id # the id of the referencing document
        # self.type = type
        self.created = datetime.now()

        #Private instance variables.
        # These are all dealt with through the getters/setters
        # labels
        self.__fp_label = None
        self.__mult_label = None
        self.__inc_label = None

        # corresponding predictions
        self.__fp_pred = None
        self.__mult_pred = None
        self.__inc_pred = None

        # dates for when label was recorded and when prediction was last made
        # same as variable names, with '_time' suffix
        self.__fp_label_time = None
        self.__mult_label_time = None
        self.__inc_label_time = None
        self.__fp_pred_time = None
        self.__mult_pred_time = None
        self.__inc_pred_time = None

    def __repr__(self):
        return "<Document: %r>" % self.id

    def set(self, var_name, var_val):
        """Generic set method for private variables using introspection
        - Currently assumes the variables are boolean (since all are in class definition)

        Args:
            var_name (str): The name of the private variable to be set, not including the underscore prefix

            var_val (bool): The value to set `self.__var_name` to.  Can be `None`

        Returns:
            None
        """
        if not isinstance(var_name, str):
            logger.error("Cannot set private variable if arg isn't type:str")
            raise TypeError
        if not isinstance(var_val, bool) and var_val is not None:
            logger.error("Cannot set variable to anything but bool or None")
            raise TypeError

        setattr(self, '__'+var_name, var_val)
        setattr(self, '__'+var_name+'_time', datetime.now())

    def get(self, var_name):
        """Generic get method for private variables using introspection

        Args:
            var_name (str): The name of the provate variable who's value is to be returned, not_including the underscore prefix

        Returns:
            var_val: The value of the variable
        """
        if not isinstance(var_name, str):
            logger.error("Cannot get private variable if name passed isn't string")
            raise TypeError
        if var_name[:2] == '__':
            logger.warning("var_name input expected to not have '__' prefix")
            var_name = var_name[2:]

        return getattr(self, '__'+var_name)


documents = Table("documents", metadata,
    # surrogate id and the association id
    Column('id', String(64), primary_key=True),
    Column('assoc_id', None, ForeignKey('document_associations.assoc_id',
                                        name='fk_doc_assoc_id'),
                                        nullable=False),
    # timestamp
    Column('created', DateTime, nullable=False),
    # labels from DOHMH experts
    Column('fp_label', Boolean, nullable=True),
    Column('mult_label', Boolean, nullable=True),
    Column('inc_label', Boolean, nullable=True),
    # predictions made by the system
    Column('fp_pred', Float, nullable=True),
    Column('mult_pred', Float, nullable=True),
    Column('inc_pred', Float, nullable=True),
    # associated timestamps
    Column('fp_label_time', DateTime, nullable=True),
    Column('mult_label_time', DateTime, nullable=True),
    Column('inc_label_time', DateTime, nullable=True),
    Column('fp_pred_time', DateTime, nullable=True),
    Column('mult_pred_time', DateTime, nullable=True),
    Column('inc_pred_time', DateTime, nullable=True)
)

mapper(Document, documents,
    properties={
        # map private variable names to more reasable column names (drop the '__')
        '__fp_label':documents.c.fp_label,
        '__mult_label':documents.c.mult_label,
        '__inc_label':documents.c.inc_label,
        '__fp_pred':documents.c.fp_pred,
        '__mult_pred':documents.c.mult_pred,
        '__inc_pred':documents.c.inc_pred,
        '__fp_label_time':documents.c.fp_label_time,
        '__mult_label_time':documents.c.mult_label_time,
        '__inc_label_time':documents.c.inc_label_time,
        '__fp_pred_time':documents.c.fp_pred_time,
        '__mult_pred_time':documents.c.mult_pred_time,
        '__inc_pred_time':documents.c.inc_pred_time
})

mapper(DocumentAssoc, document_associations, properties={
    'document':relation(Document, backref='association')
})

##############################
# Define sublasses down here #
##############################
class YelpReview(object):
    """ TODO: Fill in doc string for YelpReview Class"""
    def __init__(self, rating=None, text=None, user_name=None, yelp_id=None):
        self.rating=rating
        self.text = text
        self.user_name = user_name
        self.id = yelp_id
        # self.document = Document(id=yelp_id, type=yelp_reviews.name)

    def __repr__(self):
        return "<YelpReview: %r>" % self.text

yelp_reviews = Table('yelp_reviews', metadata,
    Column('id', String(64), primary_key=True),
    Column('doc_assoc_id', None, ForeignKey('document_associations.assoc_id',
                                            name='fk_rev_assoc_id'),
                                            nullable=False),
    Column('text', UnicodeText),
    Column('rating', Float),
    Column('user_name', String(255)),    
    Column('created', DateTime),
    Column('updated_at', DateTime, default=datetime.now, onupdate=datetime.now),
    Column('business_id', String(64), nullable=False),
    ForeignKeyConstraint( ['business_id'], ['businesses.id'], name='fk_rev_biz_id'),
)

mapper(YelpReview, yelp_reviews)
documentable(YelpReview, 'document')
