from database_con import SessionLocal
import models
from passlib.context import CryptContext

db = SessionLocal()

# join_user_order_table = db.query(models.Customer_login.user_Name, models.Restaurant_table.table_no_Id,
#                                  models.User_Orders.food_item_desc, models.User_Orders.person_per_table,
#                                  models.Customer_login.user_phone_number).join(models.User_Orders).on(
#     models.Customer_login.user_Id == models.User_Orders.user_Id).join(models.Restaurant_table).on(
#     models.User_Orders.user_Id == models.Restaurant_table.user_Id_no)


# join_user_order_table = db.query(models.Customer_login.user_Name, models.Restaurant_table.table_no_Id,
#                                  models.User_Orders.food_item_desc, models.User_Orders.person_per_table,
#                                  models.Customer_login.user_phone_number).join(models.User_Orders,
#                                  models.Customer_login.user_Id == models.User_Orders.user_Id).join(models.Restaurant_table,
#                                  models.User_Orders.user_Id == models.Restaurant_table.user_Id_no)
# for i, j, x, y, n in join_user_order_table:
#     print(i, j, x, y, n)

# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# pwd = pwd_context.hash("7021")
# print(pwd)

# user_order_data = db.query(models.Customer_login.user_Name, models.Restaurant_table.table_no_Id,
#                                    models.User_Orders.food_item_desc, models.User_Orders.person_per_table,
#                                    models.User_Orders.order_time, models.Customer_login.user_phone_number,
#                                    models.User_Orders.o).join(
#             models.User_Orders,
#             models.Customer_login.user_Id == models.User_Orders.user_Id).join(models.Restaurant_table,
#                                                                               models.User_Orders.user_Id == models.Restaurant_table.user_Id_no)
#
# for i in user_order_data:
#     print(i)

user_order_data = db.query(models.User_Orders).filter(models.User_Orders.order_Id == 1)

print(user_order_data)