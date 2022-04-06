from fastapi import Request, status, HTTPException, Depends, Response, APIRouter
from pdf_generator import make_pdf
from fastapi_mail_config import send_mail
from sqlalchemy.orm import Session
import oauth
import utils
import models
from oauth import Token_Exception
from database_con import get_db
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# APIRouter object to access the application routes
router = APIRouter(tags=["Admin"])

# Defining the template object for jinja2Templating to access/ render the html templates
templates = Jinja2Templates(directory="templates/")

# mounting the static files, through which fastapi can access the css and images files
router.mount("/static", StaticFiles(directory="static/"), name="static")


# Admin login generic API which accept only to request get and post
# get request returns admin login html page
# post request verify the admin credentials and return admin dashboard if it is a valid user
@router.api_route("/admin_login", status_code=status.HTTP_409_CONFLICT, methods=["GET", "POST"])
async def admin_login(request: Request, db: Session = Depends(get_db)):
    # If condition to decide the logic based on request
    if request.method == "POST":
        # Extracting the data from html form
        form_data = await request.form()
        email_id = form_data.get("email_id")
        pwd = form_data.get("pwd")

        # Retrieving data from DB based on user input through HTML form \
        # Verifying the user credential matches the user data from DB or not
        user_data = db.query(models.Admin_login).filter(
            models.Admin_login.user_Email_Id == email_id.strip()).first()

        try:
            # if user is null then raise a exception and redirect the user to login page with a message
            if not user_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except HTTPException:
            return templates.TemplateResponse("Adminpage.html",
                                              context={"request": request, "error": "Invalid Email or User Not found"}
                                              )

        try:

            # If user password doesn't match with user input then rasie a exception and redirect user to login page with a message
            if not utils.verify_pwd(pwd.strip(), user_data.user_Password):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except HTTPException:
            return templates.TemplateResponse("Adminpage.html",
                                              context={"request": request, "error": "Invalid Password"}
                                              )

        # After verification we are creating a JWT token to authorize the user for further user task
        access_token = oauth.create_access_token(data={"user_email": user_data.user_Email_Id})

        # Performing inner join query on multiple table to retrieve user data
        Customer_orders = db.query(models.Customer_login.user_Name, models.Restaurant_table.table_no_Id,
                                   models.User_Orders.food_item_desc, models.User_Orders.person_per_table,
                                   models.User_Orders.order_time, models.Customer_login.user_phone_number,
                                   models.User_Orders.order_Id).join(models.User_Orders,
                                                                     models.Customer_login.user_Id == models.User_Orders.user_Id).join(
            models.Restaurant_table,
            models.User_Orders.user_Id == models.Restaurant_table.user_Id_no)

        # returning the result template in response
        response = templates.TemplateResponse("Adminpanelpage.html",
                                              context={"request": request, "Customer_data": Customer_orders})

        # setting the cookie of logged user with access token
        response.set_cookie(key="access_token", value=access_token, httponly=True)

        # Returning the response to user with the html page and cookies in client side.
        return response

    else:
        # Request is get, therefore returning login page
        return templates.TemplateResponse("Adminpage.html", context={"request": request})


# Admin dashboard generic API which accept only to request get and post
# get request returns admin login html page
# post request verify the admin credentials and return admin dashboard if it is a valid user
@router.api_route("/admin_dashborad", status_code=status.HTTP_409_CONFLICT, methods=["GET", "POST"])
async def admin_dashborad(request: Request, db: Session = Depends(get_db)):
    # If condition to decide the logic based on request
    if request.method == "POST":
        # Extracting the data from html form
        user_Id = request.cookies.get("access_token")

        # Checking whether the cookies are none or not
        try:
            if not user_Id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please login")
        except HTTPException as h:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": h.detail})

        # After extracting cookies from client request
        # Verifying the access token with get_admin_user
        try:
            user_id_no = oauth.get_admin_user(user_Id)
        except Token_Exception as t:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": t.detail}, status_code=status.HTTP_401_UNAUTHORIZED)

        # Performing inner join query on multiple table to retrieve user data
        Customer_orders = db.query(models.Customer_login.user_Name, models.Restaurant_table.table_no_Id,
                                   models.User_Orders.food_item_desc, models.User_Orders.person_per_table,
                                   models.User_Orders.order_time, models.Customer_login.user_phone_number,
                                   models.User_Orders.order_Id).join(models.User_Orders,
                                                                     models.Customer_login.user_Id == models.User_Orders.user_Id
                                                                     ).join(models.Restaurant_table,
                                                                            models.User_Orders.user_Id == models.Restaurant_table.user_Id_no)

        # returning the admin dashboard html page order data read from database with join query
        return templates.TemplateResponse("Adminpanelpage.html",
                                          context={"request": request, "Customer_data": Customer_orders})

    # if the request is get then it will return admin login page
    else:
        return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "please login"}, status_code=status.HTTP_401_UNAUTHORIZED)


# Billing api which will handle get and post request
@router.api_route("/billing", status_code=status.HTTP_409_CONFLICT, methods=["GET", "POST"])
async def billing(request: Request, db: Session = Depends(get_db)):

    # if the request is post then the user is sending the data, then this if condition will run
    if request.method == "POST":

        # reading the user cookies for access token
        user_Id = request.cookies.get("access_token")

        # if the user does not have any cookie the it will raise a http exception
        try:
            # if the user_Id is none then raise and return admin login page
            if not user_Id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except HTTPException:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "please login"})

        # Verifying the user_Id access token
        try:
            user_id_no = oauth.get_admin_user(user_Id)
        except Token_Exception as t:
            # if token is invalid or couldn't validate the access token then an exception will raise
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": t.detail}, status_code=status.HTTP_401_UNAUTHORIZED)

        # Since all the credential's are verified
        # With form method we are extracting html form data
        form_data = await request.form()

        # Defining the user data inside reference variable
        user_order_Id = form_data.get("order_ID")
        food_items_placed = form_data.get("food")
        amount = form_data.get("amount")

        # read the user order data based on user unique id
        user_order_data = db.query(models.User_Orders).filter(models.User_Orders.order_Id == user_order_Id).first()

        # if user_order_data is None then order id doesn't exists
        # in that case it will raise a exception and return an return billdashboard
        try:
            if not user_order_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except HTTPException:
            return templates.TemplateResponse("billdashboard.html",
                                              context={"request": request, "msg": "Invalid order_ID"})

        # reading the customer data based on user_order_data user_Id
        cust_data = db.query(models.Customer_login).filter(
            models.Customer_login.user_Id == user_order_data.user_Id).first()

        # if cust_data is none then it will raise a httpexception
        try:
            if not cust_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except HTTPException:
            return templates.TemplateResponse("billdashboard.html",
                                              context={"request": request, "msg": "User not found"})

        # creating the invoice data content
        pdf_content = [
            f"Name: {cust_data.user_Name}",
            f"food details: {food_items_placed}",
            f"Total amount: {amount}",
            f"We hope you like our buffet system",
            f"Please visit us again"
        ]

        # calling the make_pdf function to create th pdf
        make_pdf(pdf_content)

        # calling the send_mail function to mail the invoices
        try:
            send_mail(cust_data.user_Email_Id)
        except Exception:
            return templates.TemplateResponse("billdashboard.html",
                                              context={"request": request,
                                                       "msg": "Something went wrong contact developer"}, status_code=status.HTTP_409_CONFLICT)


        # removing the user booked table vlaue
        user_table_booking = db.query(models.Restaurant_table).filter(
            models.Restaurant_table.user_Id_no == user_order_data.user_Id).first()

        # setting the user_Id field to 0
        user_table_booking.user_Id_no = 0

        # performing the update operation.
        db.merge(user_table_booking)

        # Saving the changes
        db.commit()

        # since pdf is send then we don't need user_order data in order table it will perform a delete operation
        db.delete(user_order_data)

        # commit method to save the changes
        db.commit()

        # After sending the invoice mail ut will return billdashboard with the message
        return templates.TemplateResponse("billdashboard.html",
                                          context={"request": request, "msg": "Invoice as been send"})

    # if the request is get then it will check the user credential.
    elif request.method == "GET":

        # Extracting the JWT token from user side.
        user_Id = request.cookies.get("access_token")

        # Checking the access token is there or not
        try:
            # user_Id is none that means there are no access token with the request and therefore ot will raise an HTTPException
            if not user_Id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except HTTPException:
            # it will return admin login pager with the message.
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "please login"})

        try:
            # Since user_Id is not none the with below method we will verify user jwt token.
            user_id_no = oauth.get_admin_user(user_Id)
        except Token_Exception as t:
            # if the jwt token is not valid then it raise a exception and return admin login page with message
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": t.detail})

        # Since user as a valid token it will return the valid billdashoard page.
        return templates.TemplateResponse("billdashboard.html", context={"request": request})

    # if this API is hint without any cookie so it will return admin login page
    else:
        return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "please login"})


@router.api_route("/add_food_items", status_code=status.HTTP_409_CONFLICT, methods=["GET", "POST"])
async def add_food_items(request: Request, db: Session = Depends(get_db)):

    # if user request is post then run below code
    if request.method == "POST":

        # reading the JWT token form user cookie
        user_Id = request.cookies.get("access_token")

        # checking whether the token is None or not
        try:
            # if none then raise a exception
            if not user_Id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except HTTPException:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "User not found"})

        # Since token is not none then verify the admin access token
        try:
            # if token is invalid then it will raise a exception.
            user_id_no = oauth.get_admin_user(user_Id)
        except Token_Exception as t:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": t.detail}, status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)

        # Since user is authenticated we are reading the user input from html form.
        form_data = await request.form()
        food_name = form_data.get("food_name")
        food_price = form_data.get("Price")

        # setting the insert add in orm table variables
        add_food_data = models.Food_items(
            food_item=food_name,
            food_price=food_price
        )

        # Performing create operation on food item tables.
        db.add(add_food_data)

        # Saving the changes
        db.commit()

        # refreshing the data base
        db.refresh(add_food_data)

        # reading all food items from food items table
        food_item = db.query(models.Food_items).all()

        return templates.TemplateResponse("adminfooddashboard.html",
                                          context={"request": request, "food_item": food_item},
                                          status_code=status.HTTP_201_CREATED)

    elif request.method == "GET":

        user_Id = request.cookies.get("access_token")
        try:
            if not user_Id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except HTTPException:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "User not found"})

        try:
            user_id_no = oauth.get_admin_user(user_Id)
        except Token_Exception as t:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": t.detail})

        food_item = db.query(models.Food_items).all()

        # Since user as a valid token it will return the valid billdashoard page.
        return templates.TemplateResponse("adminfooddashboard.html",
                                          context={"request": request, "food_item": food_item},
                                          status_code=status.HTTP_200_OK)

    # if this API is hint without any cookie so it will return admin login page
    else:
        return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "Please login"},
                                          status_code=status.HTTP_406_NOT_ACCEPTABLE)


# This API is for update operation on food item table were admin is updating price ,food items with food_Id
@router.api_route("/update_food_items", status_code=status.HTTP_409_CONFLICT, methods=["GET", "POST"])
async def update_food_items(request: Request, db: Session = Depends(get_db)):
    # if the request by admin is post then admin is performing update operation.
    if request.method == "POST":
        # before update operation we will verify access token from cookie for validation.
        user_Id = request.cookies.get("access_token")
        try:
            # if condition to check cookie access data.
            if not user_Id:
                # if the user_Id is none then it will raise HTTPException
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        except HTTPException as o:
            # returning admin login page since user don't have any access token.
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": o.detail})

        try:
            # Verifying user access token with below method
            user_id_no = oauth.get_admin_user(user_Id)

        # if the user has invalid token it will
        except Token_Exception as t:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": t.detail})

        # Extracting form data.
        form_data = await request.form()
        item_Id = form_data.get("item_Id")
        item_name = form_data.get("item_name")
        item_price = form_data.get("item_price")

        # Check the food_Id is their in database or not.
        food_item_data = db.query(models.Food_items).filter(models.Food_items.food_Id == item_Id).first()

        # if condition to check the food_item_data is None or not.
        if not food_item_data:
            # if None then return adminfooddashboard page with a message
            return templates.TemplateResponse("adminfooddashboard.html",
                                              context={"request": request, "update_error": "Invalid food ID"},
                                              status_code=status.HTTP_204_NO_CONTENT)

        # if the admin want to update both the entity then this if condition will be true and then below operation will run
        if item_name and item_price:

            # Setting the food_item and food_price fields for update operation
            food_item_data.food_item = item_name
            food_item_data.food_price = item_price

            # updating the column data
            db.merge(food_item_data)

            # saving the changes
            db.commit()

            # refreshing the data base table
            db.refresh(food_item_data)

            # reading all food items for responsive page to show admin the food table
            food_item = db.query(models.Food_items).all()

            return templates.TemplateResponse("adminfooddashboard.html",
                                              context={"request": request, "food_item": food_item},
                                              status_code=status.HTTP_200_OK)
        # if the admin want to update food name then below code will run
        elif item_name:

            #  Setting the food_item fields for update operation
            food_item_data.food_item = item_name

            # updating the column data
            db.merge(food_item_data)

            # saving the changes
            db.commit()

            # refreshing the data base table
            db.refresh(food_item_data)

            # reading all food items for responsive page to show admin the food table
            food_item = db.query(models.Food_items).all()

            return templates.TemplateResponse("adminfooddashboard.html",
                                              context={"request": request, "food_item": food_item},
                                              status_code=status.HTTP_200_OK)
        # if the admin want to update food price then below code will run
        elif item_price:

            #  Setting the food_price fields for update operation
            food_item_data.food_price = item_price

            # updating the column data
            db.merge(food_item_data)

            # saving the changes
            db.commit()

            # refreshing the data base table
            db.refresh(food_item_data)

            # reading all food items for responsive page to show admin the food table
            food_item = db.query(models.Food_items).all()

            return templates.TemplateResponse("adminfooddashboard.html",
                                              context={"request": request, "food_item": food_item},
                                              status_code=status.HTTP_200_OK)

    else:
        return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "Please login"},
                                          status_code=status.HTTP_403_FORBIDDEN)


@router.api_route("/delete_food_items", status_code=status.HTTP_200_OK, methods=["GET", "POST"])
async def delete_food_items(request: Request, db: Session = Depends(get_db)):

    # if user request is post then below code will run
    if request.method == "POST":

        # Reading the user cookie
        user_Id = request.cookies.get("access_token")

        # if the user cookie is None then it will raise a exception.
        try:
            if not user_Id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        except HTTPException as o:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": o.detail})

        # verifying the user access token.
        try:
            # if the user token is invalid then an exception will raise
            user_id_no = oauth.get_admin_user(user_Id)
        except Token_Exception as t:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": t.detail})

        # Since all validation is done, we will read the user input.
        form_data = await request.form()
        item_Id = form_data.get("item_Id")

        # checking the food data from table with the item_id
        food_item_data = db.query(models.Food_items).filter(models.Food_items.food_Id == item_Id).first()

        # if food_item_data is None then the item_id is invalid or does not exists.
        if not food_item_data:
            return templates.TemplateResponse("adminfooddashboard.html",
                                              context={"request": request, "del_error": "Invalid food ID"},
                                              status_code=status.HTTP_204_NO_CONTENT)
        # Since food data is there we will perform delete operation.
        db.delete(food_item_data)

        # Saving the changes.
        db.commit()

        return templates.TemplateResponse("adminfooddashboard.html",
                                          context={"request": request, "del_error": "Item deleted"},
                                          status_code=status.HTTP_204_NO_CONTENT)


    else:
        return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "Please login"},
                                          status_code=status.HTTP_403_FORBIDDEN)

# This api is used to perform logout functionality
@router.api_route("/admin_logout", status_code=status.HTTP_200_OK, methods=["GET", "POST"])
def admin_logout(response: Response, request: Request):

    # if the user request is post then below code will run.
    if request.method == "POST":

        # reading the user access token from user cookie
        user_token_data = request.cookies.get("access_token")

        # if user token is none then it will raise a exception
        try:
            if not user_token_data:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        except HTTPException:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "please login"}
                                              , status_code=status.HTTP_403_FORBIDDEN)
        response = templates.TemplateResponse("Adminpage.html", context={"request": request},
                                              status_code=status.HTTP_200_OK)

        # removing the access token from cookie.
        response.delete_cookie("access_token")

        return response
    else:
        return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "Please login"},
                                          status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
