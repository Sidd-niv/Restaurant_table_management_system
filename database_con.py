from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import setting


# SQLALCHEMY_DATABASE_URL = setting.SQLALCHEMY_DATABASE_URL

# Database driver url
SQLALCHEMY_DATABASE_URL = "postgresql://tzujxpjaauzjis:c03abf26e520bb6c9ccc959e153158d42e7a562d245ba562f1b7a75a666c8f49@ec2-3-218-171-44.compute-1.amazonaws.com:5432/dalh9i1r8j5dcv"

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

