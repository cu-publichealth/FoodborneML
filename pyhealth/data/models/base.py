"""
Declare a common Base object that can be shared across files
This allows SQLAlchemy to track models referencing eachother from multiple files
"""
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()