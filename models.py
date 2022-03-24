from sqlalchemy import Column, Integer, String, DATE, ForeignKey, TIMESTAMP, text, NUMERIC
from sqlalchemy.orm import relationship
from database_con import Base


class Customer_login(Base):
    __tablename__ = "Customer_login"

    user_Id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_Name = Column(String(60), nullable=False)
    user_Email_Id = Column(String(60), primary_key=True, nullable=False)
    user_Password = Column(String(120), nullable=False,)
    user_phone_number = Column(NUMERIC(10), nullable=False)
    user_type = Column(String(30), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    # one-to-one
    table = relationship("Restaurant_table", back_populates="user_Customer", uselist=False)

    # one to many
    customer_order = relationship("User_Orders", back_populates="order")


class Food_items(Base):
    __tablename__ = "Food_items"

    food_Id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    food_items = Column(String(60), nullable=False)
    food_price = Column(Integer, nullable=False)

    # one to many
    food_items_orders = relationship("User_Orders", back_populates="food_item")


class User_Orders(Base):
    __tablename__ = "User_Orders"

    order_Id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_Id = Column(Integer, ForeignKey('Customer_login.user_Id'), nullable=True)
    food_Id = Column(Integer, ForeignKey('Food_items.food_Id'), nullable=True)
    order_date = Column(DATE, nullable=False)

    # one to one
    order = relationship("Customer_login", back_populates="customer_order")
    # many to one
    food_item = relationship("Food_items", back_populates="food_items_orders")


class Restaurant_table(Base):
    __tablename__ = "Restaurant_table"

    table_no_Id = Column(Integer, primary_key=True, nullable=False)
    user_Id = Column(Integer, ForeignKey('Customer_login.user_Id'))

    user_Customer = relationship("Customer_login", back_populates="table")



