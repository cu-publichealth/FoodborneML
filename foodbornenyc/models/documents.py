"""
Contains document models:

1. Document  (a polymorphic associative table)
2. YelpReview
3. Tweet

This inheritance pattern is closely modeled from Source:
http://techspot.zzzeek.org/2007/05/29/polymorphic-associations-with-sqlalchemy/

Document is a polymorphic parent of specific document types. It contains all of
the things we care about at document level, like labels and predictions

The children instantiate specific instances of document types,
e.g. YelpReview or Tweet

Generally avoid messing with the `document_associations` table, the
`DocumentAssoc` class, and the `documentable` function

When creating a new type of document, just create the class, table, and mapper
as usual, but then add `documentable(DocSubClass, 'document')` and the
appropriate association with correct integrity constraints will be created.
Minimal extra code.

For example:

    ```
    db = get_db_session()
    yr = db.query(YelpReview).first()

    print yr.document
    ```
"""
from datetime import datetime
import json

from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy import Float, String, UnicodeText, DateTime, Boolean, Unicode
from sqlalchemy.orm import mapper, backref, relation, class_mapper

from foodbornenyc.models.metadata import metadata
from foodbornenyc.models.locations import Location
from foodbornenyc.models.users import TwitterUser

from foodbornenyc.util.util import get_logger, xuni
logger = get_logger(__name__)


class DocumentAssoc(object):
    """The DocumentAssoc data model. Allows for polymorphic joined table
    inheritance"""
    def __init__(self, assoc_id, name):
        self.assoc_id = assoc_id
        self.type = name

document_associations = Table('document_associations', metadata,
                              Column('assoc_id', String(64), primary_key=True),
                              Column('type', String(50), nullable=False))

def documentable(cls, name):
    """documentable 'interface'. Allows any document subtype have a `document`
    attribute

    To make a class that should be associated with a generic `Document` object
    have the attribute, simply apply this function to that class.

    eg, `documentable(YelpReview, 'document')` will endow YelpReview objects
    with a `document` association through joined table inheritance

    Additionally, the polymorphic subinstance of any document can be accessed
    with `document.source`
    """
    cls_mapper = class_mapper(cls)
    table = cls_mapper.local_table
    cls_mapper.add_property('document_rel',
                            relation(DocumentAssoc,
                                     backref=backref('_backref_%s'%table.name,
                                                     uselist=False),
                                     cascade="save-update, merge, delete",
                                     lazy="joined"))

    # scalar based property decorator
    def getter(self):
        """Getter for the relationship"""
        return self.document_rel.document[0]
    def setter(self, value):
        """Setter for the relationship"""
        if self.document_rel is None:
            self.document_rel = DocumentAssoc(self.id, table.name)
        self.document_rel.document = [value]
    setattr(cls, name, property(getter, setter))

class Document(object):
    """Generic Document data model. Stores fields common between document types

    This allows for different document types to also have Document objects
    that store the common information relevant to any document type.

    These include the labels and predictions made by classifiers.
    """
    # polymorphic reference to the associated subtype object
    source = property(lambda self: getattr(self.association,
                                        '_backref_%s' % self.association.type))

    def __init__(self, doc_id):
        self.id = doc_id # the id of the referencing document
        self.created = datetime.now()

        # Private instance variables.
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

    # Generic getters and setters for various private variables
    # This allows us to do pythonic private variable incapsulation
    def empty_setter(self, varname, varval):
        """Trivial setter. Sets `varname` to `varval`"""
        setattr(self, varname, varval)

    def datetime_setter(self, varname, varval):
        """The setter makes sure that `varname`'s associated timestamp also
        gets updated"""
        self.empty_setter(varname, varval)
        vartime = varname + '_time'
        setattr(self, vartime, datetime.now())

    def empty_getter(self, varname):
        """Trivial getter"""
        return getattr(self, varname)

    def getset(varname, getter, setter):
        """Take arbitrary private varname, getter and setter functions and
        apply them to varname"""
        return property(lambda self: getter(self, varname),
                        lambda self, varval: setter(self, varname, varval))

    # make property wrapped public variables for the labels, predictions, times
    fp_label = getset("__fp_label", empty_getter, datetime_setter)
    mult_label = getset("__mult_label", empty_getter, datetime_setter)
    inc_label = getset("__inc_label", empty_getter, datetime_setter)
    fp_pred = getset("__fp_pred", empty_getter, datetime_setter)
    mult_pred = getset("__mult_pred", empty_getter, datetime_setter)
    inc_pred = getset("__inc_pred", empty_getter, datetime_setter)
    # times have trivial wrappers for now
    fp_label_time = getset("_fp_label_time", empty_getter, empty_setter)
    fp_label_time = getset("__fp_label_time", empty_getter, empty_setter)
    mult_label_time = getset("__mult_label_time", empty_getter, empty_setter)
    inc_label_time = getset("__inc_label_time", empty_getter, empty_setter)
    fp_pred_time = getset("__fp_pred_time", empty_getter, empty_setter)
    mult_pred_time = getset("__mult_pred_time", empty_getter, empty_setter)
    inc_pred_time = getset("__inc_pred_time", empty_getter, empty_setter)

documents = Table("documents", metadata,
                  # surrogate id and the association id
                  Column('id', String(64), primary_key=True),
                  Column('assoc_id', None,
                         ForeignKey('document_associations.assoc_id',
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
                  Column('inc_pred_time', DateTime, nullable=True))

mapper(Document, documents,
       properties={
           # map private variable names to more reasable column names
           # (drop the '__')
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

mapper(DocumentAssoc, document_associations,
       properties={
           'document':relation(Document,
                               backref='association',
                               cascade="save-update, merge, delete",
                               lazy='joined')
       })

##############################
# Define sublasses down here #
##############################
class YelpReview(object):
    """Data model for Yelp reviews that we get from JSON feed"""
    def __init__(self, yelp_id=None, rating=None, text=None, user_name=None):
        self.id = yelp_id
        self.rating = rating
        self.text = text
        self.user_name = user_name
        self.created = datetime.now()
        self.document = Document(yelp_id) # not sure if this jives with the
        # polymorphic property

    def __repr__(self):
        return "<YelpReview: %r>" % self.text

yelp_reviews = Table('yelp_reviews', metadata,
                     Column('id', String(64), primary_key=True),
                     Column('doc_assoc_id', None,
                            ForeignKey('document_associations.assoc_id',
                                       name='fk_rev_assoc_id'),
                            nullable=False),
                     Column('text', UnicodeText),
                     Column('rating', Float),
                     Column('user_name', String(255)),
                     Column('created', DateTime),
                     Column('updated_at', DateTime,
                            default=datetime.now, onupdate=datetime.now),
                     Column('business_id', String(64),
                            ForeignKey('businesses.id',
                                       name='fk_rev_biz_id'),
                            nullable=False))

mapper(YelpReview, yelp_reviews)
documentable(YelpReview, 'document')

class Tweet(object):
    """ Twitter data model"""
    created_format = "%a %b %d %H:%M:%S +0000 %Y"
    # created_format = '%c'
    def __init__(self,
                 text=None,
                 id_str=None,
                 in_reply_to=None,
                 retweeted_status=None,
                 user=None,
                 lang=None,
                 created_at=None,
                 location=None):
        self.id = id_str
        # don't set any of the fields that are None; this way, when an object
        # is merged with another in the db, the db info isn't overwritten
        if text: self.text = xuni(text)
        if in_reply_to: self.in_reply_to = in_reply_to
        if retweeted_status: self.retweet_of = retweeted_status
        if lang: self.lang = lang
        if created_at:
            self.created_at = datetime.strptime(created_at, self.created_format)
        if location: self.location = location
        if user: self.user = user

        self.document = Document(id_str)

    def __repr__(self):
        return self.__unicode__()
        #return self.__unicode__().encode('ascii', 'xmlcharrefreplace')

    def __unicode__(self):
        return u"<Tweet(%s, %s)>" % (self.id[-4:], self.text[:35])


tweets = Table('tweets', metadata,
               Column('id', String(64), primary_key=True),
               Column('doc_assoc_id', None,
                            ForeignKey('document_associations.assoc_id',
                                       name='fk_tweet_assoc_id'),
                            nullable=False),
               Column('text', UnicodeText),
               Column('user_id', String(64),
                      ForeignKey('twitter_users.id', name='fk_user_tweets')),
               Column('lang', Unicode),
               Column('in_reply_to_id', String(64),
                      ForeignKey('tweets.id', name='fk_reply_tweets')),
               Column('retweet_of_id', String(64),
                      ForeignKey('tweets.id', name='fk_retweeted_tweets')),
               Column('created_at', DateTime),
               Column('location_id', String(255*6),
                      ForeignKey('locations.id', name='fk_loc_tweets')))

mapper(Tweet, tweets,
       properties={
           'location': relation(Location, backref=backref('tweets')),
           'user': relation(TwitterUser, backref=backref('tweets')),
           'retweets': relation(Tweet,
               foreign_keys=[tweets.columns['retweet_of_id']],
               backref=backref('retweet_of', remote_side=tweets.columns['id'])),
           'replies': relation(Tweet,
               foreign_keys=[tweets.columns['in_reply_to_id']],
               backref=backref('in_reply_to', remote_side=tweets.columns['id']))
       })

documentable(Tweet, 'document')
