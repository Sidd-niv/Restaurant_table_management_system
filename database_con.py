from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import setting


# Database driver url
SQLALCHEMY_DATABASE_URL = setting.SQLALCHEMY_DATABASE_URL

# Connecting database
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This will create all necessary table in database
Base = declarative_base()

# function to access session object
def get_db():
    db = SessionLocal()
    try:
        # It will return the db object.
        yield db
    finally:
        db.close()

