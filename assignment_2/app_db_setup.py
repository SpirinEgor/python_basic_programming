from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///BoardGame.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=True,
                                         autoflush=True,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import models
    import app_db_creator
    Base.metadata.create_all(bind=engine)
