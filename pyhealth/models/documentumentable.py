"""
The document model class, and its subclasses:

1. YelpReview
2. Tweet

"""
from datetime import datetime

from sqlalchemy import Column, Table, event
from sqlalchemy import Integer, Float, String, UnicodeText, DateTime
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship, backref, relation, class_mapper

from models import metadata

""" Define sublasses and tables here"""
yelp_reviews = Table('yelp_reviews', metadata,
    Column('yelp_id', String(255), primary_key=True),
    Column('doc_id', None, ForeignKey('documents.doc_id'), nullable=False),
    Column('text', UnicodeText),
    Column('rating', Float),
    Column('user_name', String(255)),    
    Column('updated_at', DateTime, default=datetime.now, onupdate=datetime.now),
    Column('business_id', String(255), ForeignKey('businesses.id'), nullable=False)
    )

class YelpReview(object):

    def __init__(self, rating=None, text=None, user_name=None, yelp_id=None):
        self.rating=rating
        self.text = text
        self.user_name = user_name
        self.yelp_id = yelp_id
        self.document = Document(yelp_reviews.name)

    def __repr__(self):
        return "<YelpReview: %r>" % self.text



""" Define the mappings at the bottom"""


"""
This part is probably confusing. It's drawn from this Source
Source: http://techspot.zzzeek.org/2007/05/29/polymorphic-associations-with-sqlalchemy/

It essentially automatically creates the document in the database
When you create one of it's subclasses by making sure:
 - The Document is instantiated in the subclass's __init__
 - Adds a relation between the two

"""
class Document(object):
    def __init__(self, name):
        self.type = name
    member = property(lambda self: getattr(self.association, '_backref_%s' % self.association.type))

documents = Table("documents", metadata,
    Column('doc_id', Integer, primary_key=True),
    Column('type', String(50), nullable=False)
)

def documentable(cls, name, uselist=False):
    """documentable 'interface'."""
    mapper = class_mapper(cls)
    table = mapper.local_table
    mapper.add_property('document_rel', relation(Document, backref=backref('_backref_%s' % table.name, uselist=False)))

    # scalar based property decorator
    def get(self):
        return self.document_rel.documents[0]
    def set(self, value):
        if self.document_rel is None:
            self.document_rel = Document(table.name)
        self.document_rel.documents = [value]
    setattr(cls, name, property(get, set))

mapper(Document, documents)

""" Define sublass mappings here """
mapper(YelpReview, yelp_reviews)
documentable(YelpReview, 'document', uselist=False)
