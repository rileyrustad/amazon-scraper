import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()
 
class Review(Base):
    __tablename__ = 'reviews'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    review_id = Column(Integer, primary_key=True)
    star_rating = Column(Text, nullable=False)
    review_title = Column(Text, nullable=False)
    review_date = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    
 
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///reviews.db')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)