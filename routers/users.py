from fastapi import Request, status, HTTPException, Depends, Response, APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import Oauth2
import Utils
import models
from Oauth2 import Token_Exception
from database_con import get_db
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["User"])

templates = Jinja2Templates(directory="templates/")
router.mount("/static", StaticFiles(directory="static/"), name="static")


@router.api_route("/register", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED,
                  methods=["GET", "POST"])
async def user_register(request: Request, db: Session = Depends(get_db)):
    if request.method == "POST":

        # Extracting the from data from HTML from
        form_data = await request.form()

        # saving the form user input data in reference variable
        name = form_data.get("name")
        email_id = form_data.get("email_id")
        phone = form_data.get("phone")
        pwd = form_data.get("pwd")
        new_pwd = Utils.get_Hash_pwd(pwd.strip())

        # verifying the email and phone number wheather it is already in use or not

        try:
            email_id_check = db.query(models.Customer_login).filter(
                models.Customer_login.user_Email_Id == email_id.strip()).first()

            # if the email is there in Database and used by another user or not
            # if yes raise a exception
            if email_id_check:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Already in use")
        except HTTPException:
            return templates.TemplateResponse("Registration_page.html", context={"request": request,
                                              "email_msg": "Email is already register please enter another one"})

        try:
            phone_check = db.query(models.Customer_login).filter(
                models.Customer_login.user_phone_number == phone.strip()).first()

            # if the phone number is there in Database and used by another user or not
            # if yes raise a exception
            if phone_check:
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Already in use")
        except HTTPException:
            return templates.TemplateResponse("Registration_page.html", context={"request": request,
                                              "phone_msg": "Phone number is already register please enter another one"})

        # All criteria are satisfied
        # Performing the Create operation on database with the help of sqlAlchemy
        new_user = models.Customer_login(user_Name=name.strip(),
                                         user_Email_Id=email_id.strip(),
                                         user_Password=new_pwd,
                                         user_phone_number=phone,
                                         user_type="Nrl")

        # Inserting the user data
        db.add(new_user)

        # Saving the user data in database in MySQL database
        db.commit()

        return templates.TemplateResponse("login_page.html", context={"request": request})

    else:
        return templates.TemplateResponse("Registration_page.html", context={"request": request})


@router.api_route("/login", response_class=HTMLResponse, methods=["GET", "POST"], status_code=status.HTTP_200_OK)
async def login(response: Response, request: Request, db: Session = Depends(get_db)):
    # If condition to decide the logic based on request
    if request.method == "POST":
        # Extracting the data from html form
        form_data = await request.form()
        email_id = form_data.get("email_id")
        pwd = form_data.get("pwd")

        # Retrieving data from DB based on user input through HTML form \
        # Verifying the user credential matches the user data from DB or not
        user_data = db.query(models.Customer_login).filter(
            models.Customer_login.user_Email_Id == email_id.strip()).first()

        try:
            # if user is null then raise a exception and redirect the user to login page with a message
            if not user_data:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        except HTTPException:
            return templates.TemplateResponse("login_page.html",
                                              context={"request": request, "error": "Invalid Email or User Not found"}
                                              )

        try:

            # If user password doesn't match with user input then rasie a exception and redirect user to login page with a message
            if not Utils.verify_pwd(pwd.strip(), user_data.user_Password):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        except HTTPException:
            return templates.TemplateResponse("login_page.html",
                                              context={"request": request, "error": "Invalid Password"}
                                              , status_code=status.HTTP_409_CONFLICT)

        # After verification we are creating a JWT token to authorize the user for further user task
        access_token = Oauth2.create_access_token(data={"user_Id": user_data.user_Id})

        # Reading the user name for DB to display on user dashboard
        user_name = user_data.user_Name

        # Retrieve the food items form Data base.
        food_item = db.query(models.Food_items).all()

        # Retrieving the available tables from database
        table_availiable = db.query(models.Restaurant_table).filter(models.Restaurant_table.user_Id_no == 0)

        # returning the result template in response
        response = templates.TemplateResponse("userdashbroad.html",
                                              context={"request": request, "user": user_name, "food_item": food_item,
                                                       "table_availiable": table_availiable})

        # setting the cookie of logged user with access token
        response.set_cookie(key="access_token", value=access_token, httponly=True)

        # Returning the response to user with the html page and cookies in client side.
        return response

    else:
        # Request is get, therefore returning login page
        return templates.TemplateResponse("login_page.html", context={"request": request})


@router.api_route("/user_Dashbroad", status_code=status.HTTP_409_CONFLICT, methods=["GET", "POST"])
async def user_Dashbroad(response: Response, request: Request, db: Session = Depends(get_db)):
    if request.method == "POST":

        # Extracting the cookie data from client request
        user_Id = request.cookies.get("access_token")

        # Reading all HTML form data
        form_data = await request.form()

        # Passing the HTML user input data in proper reference variable
        table_no = form_data.get("table_no")
        order_desc = form_data.get("order_desc")
        member = form_data.get("member")
        user_time = form_data.get("user_time")

        # Verifying the user credentials i.e.. JWT token for authorization
        try:
            user_id_no = Oauth2.get_current_user(user_Id)
        except Token_Exception:
            return templates.TemplateResponse("login_page.html", context={"request": request, "error": "Please login"})

        # Retrieve the user data from database
        user_data = db.query(models.Customer_login).filter(models.Customer_login.user_Id == user_id_no["id"]).first()

        # Reading the user name for DB to display on user dashboard
        user_name = user_data.user_Name

        # Retrieve the food items form Data base.
        food_item = db.query(models.Food_items).all()

        # Retrieving the available tables from database
        table_availiable = db.query(models.Restaurant_table).filter(models.Restaurant_table.user_Id_no == 0)

        # Checking whether the table is there or not in database based on user input
        user_table_booking = db.query(models.Restaurant_table).filter(
                                       models.Restaurant_table.table_no_Id == table_no).first()


        try:
            # if table is not there then it will return None.
            if not user_table_booking:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid table no.")
        except HTTPException:
            return templates.TemplateResponse("userdashbroad.html",
                                              context={"request": request, "error": "Enter a valid Table No.",
                                                       "user": user_name,
                                                       "food_item": food_item,
                                                       "table_availiable": table_availiable})


        try:
            # If the user_Id of restaurant table relation is not zero than it is used by others.
            if user_table_booking.user_Id_no != 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid table no.",)
        except HTTPException:
            return templates.TemplateResponse("userdashbroad.html",
                                              context={"request": request, "error": "Table is already booked",
                                                       "user": user_name,
                                                       "food_item": food_item,
                                                       "table_availiable": table_availiable})

        user_table_booking.user_Id_no = user_id_no["id"]

        db.merge(user_table_booking)

        db.commit()

        db.refresh(user_table_booking)


        order_data = models.User_Orders(user_Id=user_data.user_Id,
                                        food_item_desc=order_desc,
                                        person_per_table=member,
                                        order_time=user_time
                                        )
        # Inserting the user data
        db.add(order_data)

        # Saving the user data in database in MySQL database
        db.commit()

        # Refresh the DB
        db.refresh(order_data)


        food_item = db.query(models.Food_items).all()
        # Retrieving the available tables from database
        table_availiable = db.query(models.Restaurant_table).filter(models.Restaurant_table.user_Id_no == 0)

        return templates.TemplateResponse("userdashbroad.html",
                                          context={"request": request, "user": user_name,
                                                   "food_item": food_item,
                                                   "table_availiable": table_availiable})
    elif request.method == "GET":
        user_Id = request.cookies.get("access_token")

        try:
            if not user_Id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        except Token_Exception:
            return templates.TemplateResponse("login_page.html", context={"request": request, "error": "Please login"})

        try:
            user_id_no = Oauth2.get_current_user(user_Id)
        except Token_Exception:
            return templates.TemplateResponse("login_page.html", context={"request": request, "error": "Please login"})

        user_data = db.query(models.Customer_login).filter(models.Customer_login.user_Id == user_id_no["id"]).first()

        # Reading the user name for DB to display on user dashboard
        user_name = user_data.user_Name

        # Retrieve the food items form Data base.
        food_item = db.query(models.Food_items).all()

        # Retrieving the available tables from database
        table_availiable = db.query(models.Restaurant_table).filter(models.Restaurant_table.user_Id_no == 0)

        return templates.TemplateResponse("userdashbroad.html",
                                              context={"request": request, "user": user_name, "food_item": food_item,
                                                       "table_availiable": table_availiable})




@router.api_route("/myorders", status_code=status.HTTP_409_CONFLICT,  methods=["GET", "POST"])
async def myorders(request: Request, db: Session = Depends(get_db)):

        if request.method == "POST":
            user_Id = request.cookies.get("access_token")

            if user_Id:
                try:
                    user_id_no = Oauth2.get_current_user(user_Id)
                except Token_Exception:
                    return templates.TemplateResponse("login_page.html",
                                                      context={"request": request, "error": "Please login"})

                user_order_data = db.query(models.User_Orders).filter(
                    models.User_Orders.user_Id == user_id_no["id"]).first()

                user_booked_table = db.query(models.Restaurant_table).filter(models.Restaurant_table.user_Id_no == user_id_no["id"]).first()

                if not user_order_data:
                    user_data = db.query(models.Customer_login).filter(
                        models.Customer_login.user_Id == user_id_no["id"]).first()

                    # Reading the user name for DB to display on user dashboard
                    user_name = user_data.user_Name

                    # Retrieve the food items form Data base.
                    food_item = db.query(models.Food_items).all()

                    # Retrieving the available tables from database
                    table_availiable = db.query(models.Restaurant_table).filter(models.Restaurant_table.user_Id_no == 0)

                    return templates.TemplateResponse("userdashbroad.html",
                                                      context={"request": request, "error": "You didn't placed any order",
                                                               "user": user_name, "food_item": food_item,
                                                               "table_availiable": table_availiable
                                                               })

                return templates.TemplateResponse("myorderspage.html",
                                                  context={"request": request,
                                                           "food_item_desc": user_order_data.food_item_desc,
                                                           "person_per_table": user_order_data.person_per_table,
                                                           "order_time": user_order_data.order_time,
                                                           "table": user_booked_table.table_no_Id})

            else:
                return templates.TemplateResponse("login_page.html",
                                                  context={"request": request, "error": "Please login"})
        else:
            return templates.TemplateResponse("login_page.html",
                                              context={"request": request, "error": "Please login"})

@router.post("/deleteOrder", status_code=status.HTTP_200_OK)
def deleteOrder(request: Request, db: Session = Depends(get_db)):
    user_Id = request.cookies.get("access_token")
    if user_Id:
        try:
            user_id_no = Oauth2.get_current_user(user_Id)
        except Token_Exception:
            return templates.TemplateResponse("login_page.html",
                                              context={"request": request, "error": "Please login"})

        order_data = db.query(models.User_Orders).filter(models.User_Orders.user_Id == user_id_no["id"]).first()

        db.delete(order_data)

        db.commit()

        user_table_booking = db.query(models.Restaurant_table).filter(
            models.Restaurant_table.user_Id_no == user_id_no["id"]).first()

        user_table_booking.user_Id_no = 0

        db.merge(user_table_booking)

        db.commit()

        user_data = db.query(models.Customer_login).filter(models.Customer_login.user_Id == user_id_no["id"]).first()

        # Reading the user name for DB to display on user dashboard
        user_name = user_data.user_Name

        # Retrieve the food items form Data base.
        food_item = db.query(models.Food_items).all()

        # Retrieving the available tables from database
        table_availiable = db.query(models.Restaurant_table).filter(models.Restaurant_table.user_Id_no == 0)

        return templates.TemplateResponse("userdashbroad.html",
                                          context={"request": request, "user": user_name, "food_item": food_item,
                                                   "table_availiable": table_availiable})








@router.api_route("/user_logout", status_code=status.HTTP_200_OK, methods=["GET", "POST"])
async def user_logout(response: Response, request: Request):
    if request.method == "POST":
        user_token_data = request.cookies.get("access_token")
        try:
            if not user_token_data:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        except HTTPException:
            return templates.TemplateResponse("login_page.html", context={"request": request, "error": "Please Login"}
                                              , status_code=status.HTTP_403_FORBIDDEN)
        response = templates.TemplateResponse("login_page.html", context={"request": request},
                                              status_code=status.HTTP_200_OK)
        response.delete_cookie("access_token")

        return response
    else:
        return templates.TemplateResponse("login_page.html", context={"request": request, "error": "Please login"},
                                          status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
