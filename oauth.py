from jose import JWTError, jwt
import secrets
from datetime import datetime, timedelta
from fastapi import status, HTTPException
import models
from database_con import SessionLocal
from schemas import Token_data, Token_access_data
from config import setting

# Object of SessionLocal
db = SessionLocal()


# Custom Exception
class Token_Exception(HTTPException):
    pass

# Secret Key references variable
SECERT_KEY = setting.secert_key

# Algorithm
ALGORITHM = setting.algorithm

# Expire time
ACCESS_TOKEN_EXPIRE_TIME = setting.access_token_expire_time

# verifying the user id from database
def verify_user_db(user_ID: int):
    # reading the user data based on User_Id
    user_check = db.query(models.Customer_login).filter(models.Customer_login.user_Id == user_ID).first()

    # if user is not none then it will return true
    if user_check:
        return True
    else:
        return False


# verifying the admin email from database
def verify_admin_db(user_email: str):
    # reading the user data based on User_Id
    user_check = db.query(models.Admin_login).filter(models.Admin_login.user_Email_Id == user_email).first()

    # if user is not none then it will return true
    if user_check:
        return True
    else:
        return False


# Function to create JWT token
def create_access_token(data: dict):
    # Copying the user data dict in reference variable
    to_encode = data.copy()

    # Declaring th expire time stamp for JWT token
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_TIME)

    # adding the expire time stamp in user data dictionary
    to_encode.update({"exp": expire})

    # Creating i.e..  Encoding the JWT token
    encoded_token = jwt.encode(to_encode, SECERT_KEY, algorithm=ALGORITHM)

    # Return the encoded token
    return encoded_token


# function to verify user JWT token
def verify_access_token(token: str):
    try:

        # Decoding the JWT token to read user data from  cookie
        payload = jwt.decode(token, SECERT_KEY, algorithms=[ALGORITHM])

        # Declaring the id reference variable with user data from token
        token_id: str = payload.get("user_Id")

        # if the user data is not there in token then raise a HTTPException
        if id is None:
            raise Token_Exception(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail="Could not validate credentials")

        # Save the user data in pydantic class object and converting it into dictionary data structure
        token_data = Token_data(id=token_id).dict()

        # verifying the user is there in database or not
        if verify_user_db(token_data['id']) == False:
            raise Token_Exception(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail="Could not validate credentials")

    except JWTError:
        raise Token_Exception(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail="Could not validate credentials")

    # hence there is no exception we can pass the user data from token
    return token_data


# Invoking the token verification function
def get_current_user(token: str):
    return verify_access_token(token)


# function to verify user JWT token
def verify_admin_token(token: str):
    try:
        # Decoding the JWT token to read admin data from  cookie
        payload = jwt.decode(token, SECERT_KEY, algorithms=[ALGORITHM])

        # Declaring the user_email reference variable with user data from token
        user_email: str = payload.get("user_email")

        # if the user data is not there in token then raise a HTTPException
        if user_email is None:
            raise Token_Exception(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

        # Save the user data in pydantic class object and converting it into dictionary data structure
        token_data = Token_access_data(user_email=user_email).dict()

        # verifying the admin is there in database or not
        if verify_admin_db(token_data['user_email']) == False:
            raise Token_Exception(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail="Could not validate credentials")

    except JWTError:
        raise Token_Exception(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, detail="Could not validate credentials")

    # hence there is no exception we can pass the admin data from token
    return token_data


# Invoking the token verification function
def get_admin_user(token: str):
    return verify_admin_token(token)
