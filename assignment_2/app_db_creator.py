from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///BoardGame.db', echo=True)
Base = declarative_base()


class BoardGame(Base):
    __tablename__ = "BoardGame"
    id = Column(Integer, primary_key=True)
    rank = Column(Integer)
    title = Column(String)
    rating = Column(String)
    price = Column(String)
    stock = Column(String)


Base.metadata.create_all(engine)
