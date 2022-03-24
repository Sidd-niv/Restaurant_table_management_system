from jose import JWTError, jwt
import secrets
from datetime import datetime, timedelta
from fastapi import  status, HTTPException

import models
from database_con import SessionLocal
from schemas import Token_data

db = SessionLocal()

# Custom Exception
class Token_Exception(HTTPException):
    pass

# Secret Key
SECERT_KEY = secrets.token_bytes(16)

# Algorithm
ALGORITHM = "HS256"

# Expire time
ACCESS_TOKEN_EXPIRE_TIME = 60


# Function to create JWT token

def verify_user_db(user_ID: int):
    user_check = db.query(models.Customer_login).filter(models.Customer_login.user_Id == user_ID).first()
    if user_check:
        return  True
    else:
        return False


def create_access_token(data: dict):
    to_encode = data.copy()
    print(to_encode)

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_TIME)
    to_encode.update({"exp": expire})

    encoded_token = jwt.encode(to_encode, SECERT_KEY, algorithm=ALGORITHM)

    return encoded_token


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECERT_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_Id")

        if id is None:
            raise Token_Exception(status_code=status.HTTP_404_NOT_FOUND, detail="Could not validate credentials")

        token_data = Token_data(id=id).dict()

        if verify_user_db(token_data['id']) == False:
            raise Token_Exception(status_code=status.HTTP_404_NOT_FOUND, detail="Could not validate credentials")

    except JWTError:
        raise Token_Exception(status_code=status.HTTP_404_NOT_FOUND, detail="Could not validate credentials")

    return token_data


def get_current_user(token: str):
    return verify_access_token(token)


