import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()
 
class Review(Base):
    __tablename__ = 'reviews'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    review_id = Column(Text, primary_key=True)
    star_rating = Column(Text, nullable=False)
    review_title = Column(Text, nullable=False)
    review_date = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    product_ASIN = Column(Text, nullable=False)

class Category(Base):
    __tablename__ = 'categories'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    category_name = Column(Text, primary_key=True)
    completed = Column(Boolean, nullable=False)
    
class Product(Base):
    __tablename__ = 'products'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    product_ASIN = Column(Text, primary_key=True)
    completed = Column(Boolean, nullable=False)
    
 
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///reviews.db')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)