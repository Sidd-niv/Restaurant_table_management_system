from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:Sidd@localhost/Restaurant_Table_Management_System_DB"

# Database driver url
# SQLALCHEMY_DATABASE_URL = "postgresql://aujdjwwviinzbk:a96c3930e1955458823c071e6a7fe937f9b9e0bab51ded4cc14240bd4dcb2ebb@ec2-44-194-4-127.compute-1.amazonaws.com:5432/da17jrcbfpjgub"

# Connecting database
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# factory function  that returns a base class
Base = declarative_base()

# function to access session object
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
