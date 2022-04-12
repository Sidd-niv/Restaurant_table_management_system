from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import setting


SQLALCHEMY_DATABASE_URL = setting.SQLALCHEMY_DATABASE_URL

# Database driver url
# SQLALCHEMY_DATABASE_URL = "postgresql://aujdjwwviinzbk:a96c3930e1955458823c071e6a7fe937f9b9e0bab51ded4cc14240bd4dcb2ebb@ec2-44-194-4-127.compute-1.amazonaws.com:5432/da17jrcbfpjgub"

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

