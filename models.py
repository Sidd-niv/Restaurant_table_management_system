from sqlalchemy import Column, Integer, String, DATE, ForeignKey, TIMESTAMP, text, NUMERIC
from sqlalchemy.orm import relationship
from database_con import Base


# ORM models to map the relational world schemas with OOP's world classes

# Customer login table entity class
class Customer_login(Base):
    # Specifying the table name
    __tablename__ = "Customer_login"

    # mapping the schemas fields through instances variable
    user_Id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_Name = Column(String(60), nullable=False)
    user_Email_Id = Column(String(60), primary_key=False, nullable=False)
    user_Password = Column(String(120), nullable=False,)
    user_phone_number = Column(NUMERIC(10), nullable=False)
    user_type = Column(String(30), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


    # one to many
    customer_order = relationship("User_Orders", back_populates="order", cascade="all, delete",)


# Food_items table entity class
class Food_items(Base):
    # Specifying the table name
    __tablename__ = "Food_items"

    # mapping the schemas fields through instances variable
    food_Id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    food_item = Column(String(60), nullable=False)
    food_price = Column(Integer, nullable=False)


# User_Orders table entity class
class User_Orders(Base):
    # Specifying the table name
    __tablename__ = "User_Orders"

    # mapping the schemas fields through instances variable
    order_Id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_Id = Column(Integer, ForeignKey('Customer_login.user_Id', ondelete="CASCADE"), nullable=True)
    food_item_desc = Column(String(120), nullable=True)
    person_per_table = Column(String(120), nullable=True)
    order_time = Column(String(60), nullable=False)

    # one to one relation
    order = relationship("Customer_login", back_populates="customer_order")



# Restaurant_table table entity class
class Restaurant_table(Base):
    # Specifying the table name
    __tablename__ = "Restaurant_table"

    # mapping the schemas fields through instances variable
    table_no_Id = Column(Integer, primary_key=True, nullable=False)
    user_Id_no = Column(Integer, nullable=True)

# Restaurant_table table entity class
class Admin_login(Base):
    # Specifying the table name
    __tablename__ = "Admin_login"

    # mapping the schemas fields through instances variable
    user_Email_Id = Column(String(60), primary_key=True, nullable=False)
    user_Password = Column(String(120), nullable=False, )


