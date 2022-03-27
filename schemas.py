from typing import Optional
from pydantic import BaseModel, EmailStr


class User_Create(BaseModel):
    user_Name: str
    user_Email_Id: EmailStr
    user_Password: str
    user_phone_number: int
    user_type: Optional[str] = "Nrl"

    class Config:
        orm_mode = True


class User_Login(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str


class Token_data(BaseModel):
    id: Optional[int] = None


class Token_access_data(BaseModel):
    user_email: Optional[str] = None


class User_Orders_re(BaseModel):
    table_no_id: int
    food_items: str
    quantity: int
    time: str

    class Config:
        orm_mode = True


class Food_(BaseModel):
    food_items: str
    food_price: int

    class Config:
        orm_mode = True
