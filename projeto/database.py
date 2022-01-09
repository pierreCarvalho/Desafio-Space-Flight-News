from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

# Create a sqlite engine instance
engine = create_engine("sqlite:///database.db")

# Create a DeclarativeMeta instance
Base = declarative_base()


class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    featured = Column(Boolean)
    title = Column(String(256))
    url = Column(String(256))
    imageUrl = Column(String(256))
    newsSite = Column(String(256))
    summary = Column(String(256))
    publishedAt = Column(String(256))

class Event(Base):
    __tablename__ = 'Events'
    id = Column(Integer, primary_key=True)
    provider = Column(String(256))
    article_id = Column(Integer, ForeignKey("articles.id"))

class Launch(Base):
    __tablename__ = 'Launches'
    id = Column(Integer, primary_key=True)
    provider = Column(String(256))
    article_id = Column(Integer, ForeignKey("articles.id"))

