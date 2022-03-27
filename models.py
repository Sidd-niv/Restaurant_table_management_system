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


    # one to many
    customer_order = relationship("User_Orders", back_populates="order", cascade="all, delete",)



class Food_items(Base):
    __tablename__ = "Food_items"

    food_Id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    food_item = Column(String(60), nullable=False)
    food_price = Column(Integer, nullable=False)


class User_Orders(Base):
    __tablename__ = "User_Orders"

    order_Id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_Id = Column(Integer, ForeignKey('Customer_login.user_Id', ondelete="CASCADE"), nullable=True)
    food_item_desc = Column(String(120), nullable=True)
    person_per_table = Column(String(120), nullable=True)
    order_time = Column(String(60), nullable=False)

    # one to one
    order = relationship("Customer_login", back_populates="customer_order")




class Restaurant_table(Base):
    __tablename__ = "Restaurant_table"

    table_no_Id = Column(Integer, primary_key=True, nullable=False)
    user_Id_no = Column(Integer, nullable=True)

class Admin_login(Base):
    __tablename__ = "Admin_login"

    user_Email_Id = Column(String(60), primary_key=True, nullable=False)
    user_Password = Column(String(120), nullable=False, )


