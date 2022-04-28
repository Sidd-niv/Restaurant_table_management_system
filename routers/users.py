from fastapi import Request, status, HTTPException, Depends, Response, APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pwd_hashing_and_jwt_token import oauth, utils
from database_connections_and_orm_sechemas import models
from pwd_hashing_and_jwt_token.oauth import Token_Exception
from database_connections_and_orm_sechemas.database_con import get_db
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# This object will allow us to create the API
router = APIRouter(tags=["User"])

# Template object to access the html templates
templates = Jinja2Templates(directory="templates/")
router.mount("/static", StaticFiles(directory="static/"), name="static")


# user_register API will return register page we get request is made.
# After making a post request it will perform create operation on customer_login table to create new user but after
# performing some validation
@router.api_route("/register", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED, methods=["GET", "POST"])
async def user_register(request: Request, db: Session = Depends(get_db)):
    if request.method == "POST":
        # Extracting the from data from HTML from
        html_form_data = await request.form()
        # saving the form user input data in reference variable
        new_user_name = html_form_data.get("name")  # User name
        new_user_email_id = html_form_data.get("email_id")  # User email
        new_user_phone_no = html_form_data.get("phone")  # User phone number
        new_user_hashed_pwd = utils.get_Hash_pwd(
            html_form_data.get("pwd").strip())  # User password which hashed directly with hash function.

        # verifying the email and phone number whether it is already in use or not
        try:
            email_id_check = db.query(models.Customer_login).filter(
                models.Customer_login.user_Email_Id == new_user_email_id.strip()).first()

            # if the email is there in Database and used by another user or not
            # if yes raise a exception
            if email_id_check:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Already in use")
        except HTTPException as h:
            return templates.TemplateResponse("Registration_page.html", status_code=h.status_code
                                              , context={"request": request,
                                                         "email_msg": "Email is already register please enter another one"})

        try:
            phone_check = db.query(models.Customer_login).filter(
                models.Customer_login.user_phone_number == new_user_phone_no.strip()).first()

            # if the phone number is there in Database and used by another user or not
            # if yes raise a exception
            if phone_check:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)
        except HTTPException as h:
            return templates.TemplateResponse("Registration_page.html",
                                              status_code=h.status_code,
                                              context={"request": request,
                                                       "phone_msg": "Phone number is already register please enter another one"})

        # All criteria are satisfied
        # Performing the Create operation on database with the help of sqlAlchemy
        new_user_data_object = models.Customer_login(user_Name=new_user_name.strip(),
                                         user_Email_Id=new_user_email_id.strip(),
                                         user_Password=new_user_hashed_pwd,
                                         user_phone_number=new_user_phone_no,
                                         user_type="Nrl")

        # Inserting the user data
        db.add(new_user_data_object)

        # Saving the user data in database i.e.. MySQL database
        db.commit()

        # Returning the login html template
        return templates.TemplateResponse("login_page.html", status_code=status.HTTP_201_CREATED,
                                          context={"request": request})

    else:
        # Since request is get we are return the registration html page
        return templates.TemplateResponse("Registration_page.html", status_code=status.HTTP_302_FOUND,
                                          context={"request": request})

# This API will be used to login, it will perform authentication
@router.api_route("/login", response_class=HTMLResponse, methods=["GET", "POST"], status_code=status.HTTP_200_OK)
async def login(response: Response, request: Request, db: Session = Depends(get_db)):

    # If condition to decide the logic based on request
    if request.method == "POST":
        # Extracting the data from html form
        html_form_data = await request.form()
        user_email_id = html_form_data.get("email_id")  # user email id form login form
        user_pwd = html_form_data.get("pwd")  # user password form login form

        # Verifying the user credential matches the user data from DB or not
        user_data = db.query(models.Customer_login).filter(
            models.Customer_login.user_Email_Id == user_email_id.strip()).first()
        # user_data contains the matched data from DB based on email_id from html form

        # Verifying the user credential matches the user data from DB or not
        try:
            # if user is null then raise a exception and redirect the user to login page with a message
            if not user_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except HTTPException as h:
            return templates.TemplateResponse("login_page.html", status_code=h.status_code,
                                              context={"request": request, "error": "Invalid Email or User Not found"}
                                              )

        try:
            # If user password doesn't match with user input then rasie a exception and redirect user to login page with a message
            if not utils.verify_pwd(user_pwd.strip(), user_data.user_Password):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except HTTPException as h:
            return templates.TemplateResponse("login_page.html",
                                              status_code=h.status_code,
                                              context={"request": request, "error": "Invalid Password"})

        # After verification we are creating a JWT token to authorize the user for further user task
        access_token = oauth.create_access_token(data={"user_Id": user_data.user_Id})

        # Reading the user name for DB to display on user dashboard
        user_name = user_data.user_Name

        # Retrieve the food items form Data base.
        food_item = db.query(models.Food_items).all()

        # Retrieving the available tables from database
        table_available_in_db = db.query(models.Restaurant_table).filter(models.Restaurant_table.user_Id_no == 0)

        # returning the result template in response
        response = templates.TemplateResponse("userdashbroad.html", status_code=status.HTTP_302_FOUND,
                                              context={"request": request, "user": user_name, "food_item": food_item,
                                                       "table_availiable": table_available_in_db})

        # setting the cookie of logged user with access token
        response.set_cookie(key="access_token", value=access_token, httponly=True)

        # Returning the response to user with the html page and cookies in client side.
        return response

    else:
        # Request is get, therefore returning login page
        return templates.TemplateResponse("login_page.html", context={"request": request})


# user_Dashbroad API will be use to register the user table booking order.
@router.api_route("/user_Dashbroad", status_code=status.HTTP_409_CONFLICT, methods=["GET", "POST"])
async def user_Dashbroad(response: Response, request: Request, db: Session = Depends(get_db)):
    if request.method == "POST":

        # Extracting the cookie data from client request
        user_Id = request.cookies.get("access_token")

        # Reading all HTML form data
        html_form_data = await request.form()

        # Passing the HTML user input data in proper reference variable
        user_booked_table_no = html_form_data.get("table_no")
        user_food_order_desc = html_form_data.get("order_desc")
        no_of_members = html_form_data.get("member")
        user_time = html_form_data.get("user_time")

        try:
            # if the user cookie is none they raise a exception
            if not user_Id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except HTTPException as h:
            return templates.TemplateResponse("login_page.html",
                                              status_code=h.status_code,
                                              context={"request": request, "error": "Please login"})

        # Verifying the user credentials i.e.. JWT token for authorization
        try:
            user_id_no = oauth.get_current_user(user_Id)
        except Token_Exception as t:
            return templates.TemplateResponse("login_page.html", status_code=t.status_code
                                              , context={"request": request, "error": t.detail})

        # Retrieve the user data from database
        user_data = db.query(models.Customer_login).filter(models.Customer_login.user_Id == user_id_no["id"]).first()

        # Reading the user name for DB to display on user dashboard
        user_name = user_data.user_Name

        # Retrieving the available tables from database
        table_available_in_db = db.query(models.Restaurant_table).filter(models.Restaurant_table.user_Id_no == 0)

        # Retrieve the food items form Data base for food menu.
        food_item = db.query(models.Food_items).all()

        # Read whether the user has booked the booked the table or not
        user_order_check = db.query(models.User_Orders).filter(models.User_Orders.user_Id == user_id_no["id"]).first()

        try:
            # if user as booked the table already they it will redirect to dash board with below message
            if user_order_check:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You have already booked your table")
        except HTTPException as h:
            return templates.TemplateResponse("userdashbroad.html", status_code=h.status_code,
                                              context={"request": request, "error": h.detail,
                                                       "user": user_name,
                                                       "food_item": food_item,
                                                       "table_availiable": table_available_in_db})

        # Checking whether the table is there or not in database based on user input
        user_table_booking = db.query(models.Restaurant_table).filter(
            models.Restaurant_table.table_no_Id == user_booked_table_no).first()

        try:
            # if table is not there then it will return None.
            if not user_table_booking:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except HTTPException as h:
            return templates.TemplateResponse("userdashbroad.html", status_code=h.status_code,
                                              context={"request": request, "error": "Enter a valid Table No.",
                                                       "user": user_name,
                                                       "food_item": food_item,
                                                       "table_availiable": table_available_in_db})

        try:
            # If the user_Id of restaurant table relation is not zero than it is used by others.
            if user_table_booking.user_Id_no != 0:
                raise HTTPException(status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        except HTTPException as h:
            return templates.TemplateResponse("userdashbroad.html", status_code=h.status_code,
                                              context={"request": request, "error": "Table is already booked",
                                                       "user": user_name,
                                                       "food_item": food_item,
                                                       "table_availiable": table_available_in_db})

        # Since all criteria are satisfy now we can proceed with create operation

        # updating the restaurant table data for user
        user_table_booking.user_Id_no = user_id_no["id"]

        # After setting user_Id field to customer login table id we are booking the table for user.
        db.merge(user_table_booking)

        # Saving the changes/ data
        db.commit()

        # refresh the data base.
        db.refresh(user_table_booking)

        # initializing the user_order columns to perform create operation.
        order_data = models.User_Orders(user_Id=user_data.user_Id,
                                        food_item_desc=user_food_order_desc,
                                        person_per_table=no_of_members,
                                        order_time=user_time
                                        )
        # Inserting the user data
        db.add(order_data)

        # Saving the user data in database in MySQL database
        db.commit()

        # Refresh the DB
        db.refresh(order_data)

        # reading all the food items from database
        food_item = db.query(models.Food_items).all()

        # Retrieving the available tables from database
        table_availiable = db.query(models.Restaurant_table).filter(models.Restaurant_table.user_Id_no == 0)

        # returning the userdashbroad with food menu data and table data
        return templates.TemplateResponse("userdashbroad.html", status_code=status.HTTP_201_CREATED,
                                          context={"request": request, "user": user_name,
                                                   "food_item": food_item,
                                                   "table_availiable": table_availiable})

    # if the user request is get then this logic will run.
    elif request.method == "GET":

        # reading the cookie data for JWT token.
        user_Id = request.cookies.get("access_token")

        try:
            # if the user cookie is none they raise a exception
            if not user_Id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except HTTPException as h:
            return templates.TemplateResponse("login_page.html", status_code=h.status_code,
                                              context={"request": request, "error": "Please login"})

        try:
            # if user as access token they verify it
            user_id_no = oauth.get_current_user(user_Id)
        except Token_Exception as t:
            return templates.TemplateResponse("login_page.html",
                                              status_code=t.status_code,
                                              context={"request": request, "error": t.detail})

        # After authentication read user info from data base.
        user_data = db.query(models.Customer_login).filter(models.Customer_login.user_Id == user_id_no["id"]).first()

        # Reading the user name for DB to display on user dashboard
        user_name = user_data.user_Name

        # Retrieve the food items form Data base.
        food_item = db.query(models.Food_items).all()

        # Retrieving the available tables from database
        table_availiable = db.query(models.Restaurant_table).filter(models.Restaurant_table.user_Id_no == 0)

        return templates.TemplateResponse("userdashbroad.html", status_code=status.HTTP_200_OK,
                                          context={"request": request, "user": user_name, "food_item": food_item,
                                                   "table_availiable": table_availiable})


# This API is to allow user to view the booking details
@router.api_route("/myorders", status_code=status.HTTP_409_CONFLICT, methods=["GET", "POST"])
async def myorders(request: Request, db: Session = Depends(get_db)):
    # if the user request is post then below if block code will run
    if request.method == "POST":
        # extracting user access token from user cookie
        user_Id = request.cookies.get("access_token")

        # user access token is not None.
        if user_Id:

            # Verify the access token since user access token is not none.
            try:
                # If access token is invalid it will raise a token exception.
                user_id_no = oauth.get_current_user(user_Id)
            except Token_Exception as t:
                return templates.TemplateResponse("login_page.html", status_code=t.status_code,
                                                  context={"request": request, "error": "Please login"})

            # Since user token is valid we will perform a read operation with user_Id
            user_order_data = db.query(models.User_Orders).filter(
                models.User_Orders.user_Id == user_id_no["id"]).first()

            # Reading the user booked table from restaurant table
            user_booked_table = db.query(models.Restaurant_table).filter(
                models.Restaurant_table.user_Id_no == user_id_no["id"]).first()

            # if user_order_data is None.
            if not user_order_data:
                # Reading user info from database
                user_data = db.query(models.Customer_login).filter(
                    models.Customer_login.user_Id == user_id_no["id"]).first()

                # Reading the user name for DB to display on user dashboard
                user_name = user_data.user_Name

                # Retrieve the food items form Data base.
                food_item = db.query(models.Food_items).all()

                # Retrieving the available tables from database
                table_available_in_db = db.query(models.Restaurant_table).filter(models.Restaurant_table.user_Id_no == 0)

                # Since user order data is none we are returning the userdashborad with the below message
                return templates.TemplateResponse("userdashbroad.html", status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                                  context={"request": request, "error": "You didn't placed any order",
                                                           "user": user_name, "food_item": food_item,
                                                           "table_availiable": table_available_in_db,
                                                           })
            # if user found return my order page to view
            return templates.TemplateResponse("myorderspage.html",
                                              status_code=status.HTTP_302_FOUND,
                                              context={"request": request,
                                                       "food_item_desc": user_order_data.food_item_desc,
                                                       "person_per_table": user_order_data.person_per_table,
                                                       "order_time": user_order_data.order_time,
                                                       "table": user_booked_table.table_no_Id})

        # user access token is None then we are redirecting user to login page.
        else:
            return templates.TemplateResponse("login_page.html",
                                              status_code=status.HTTP_401_UNAUTHORIZED,
                                              context={"request": request, "error": "Please login"})

    else:
        return templates.TemplateResponse("login_page.html",
                                          context={"request": request, "error": "Please login"})


# This API will delete the user order from database.
@router.post("/deleteOrder", status_code=status.HTTP_200_OK)
def deleteOrder(request: Request, db: Session = Depends(get_db)):
    # extracting the user access token from cookie
    user_Id = request.cookies.get("access_token")

    # if user token is not None
    if user_Id:
        try:
            # verifying the JWT token if invalid then it will raise a exception
            user_id_no = oauth.get_current_user(user_Id)
        except Token_Exception as t:
            return templates.TemplateResponse("login_page.html", status_code=t.status_code,
                                              context={"request": request, "error": "Please login"})

        # Since user is authenticated then we will try to read user data  from user order table
        order_data = db.query(models.User_Orders).filter(models.User_Orders.user_Id == user_id_no["id"]).first()

        # Since order data is there we will perform delete operation
        db.delete(order_data)

        # Saving the changes
        db.commit()

        # Now to will rest the restaurant table to 0

        # Read the user table booked data
        user_table_booking = db.query(models.Restaurant_table).filter(
            models.Restaurant_table.user_Id_no == user_id_no["id"]).first()

        # setting user_Id field to 0
        user_table_booking.user_Id_no = 0

        # updating the table data
        db.merge(user_table_booking)

        # saving the changes
        db.commit()

        # reading the user data from customer login table.
        user_data = db.query(models.Customer_login).filter(models.Customer_login.user_Id == user_id_no["id"]).first()

        # Reading the user name for DB to display on user dashboard
        user_name = user_data.user_Name

        # Retrieve the food items form Data base.
        food_item = db.query(models.Food_items).all()

        # Retrieving the available tables from database
        table_available_in_db = db.query(models.Restaurant_table).filter(models.Restaurant_table.user_Id_no == 0)

        return templates.TemplateResponse("userdashbroad.html", status_code=status.HTTP_201_CREATED,
                                          context={"request": request, "user": user_name, "food_item": food_item,
                                                   "table_availiable": table_available_in_db})


# This API will remove the user access token from user cookie for logout functionality
@router.api_route("/user_logout", status_code=status.HTTP_200_OK, methods=["GET", "POST"])
async def user_logout(response: Response, request: Request):
    # If user request is post then run the below if part code.
    if request.method == "POST":

        # reading the access token from user cookies to authenticate user
        user_token_data = request.cookies.get("access_token")
        try:
            # if user token is None then raise a exception
            if not user_token_data:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        except HTTPException as h:
            return templates.TemplateResponse("login_page.html", status_code=h.status_code,
                                              context={"request": request, "error": "Please Login"})

        # saving the return html page in response
        response = templates.TemplateResponse("login_page.html", context={"request": request},
                                              status_code=status.HTTP_200_OK)

        # deleting the cookie with response
        response.delete_cookie("access_token")

        # Return the response.
        return response
    else:
        return templates.TemplateResponse("login_page.html", status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                          context={"request": request, "error": "Please login"},
                                          )
