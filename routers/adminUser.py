from fastapi import Request, status, HTTPException, Depends, Response, APIRouter
from fastapi.responses import HTMLResponse
from pdf_generator import make_pdf
from fastapi_mail_config import send_mail
from sqlalchemy.orm import Session
import Oauth2
import Utils
import models
from Oauth2 import Token_Exception
from database_con import get_db
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Admin"])

templates = Jinja2Templates(directory="templates/")
router.mount("/static", StaticFiles(directory="static/"), name="static")


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
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        except HTTPException:
            return templates.TemplateResponse("Adminpage.html",
                                              context={"request": request, "error": "Invalid Email or User Not found"}
                                              )

        try:

            # If user password doesn't match with user input then rasie a exception and redirect user to login page with a message
            if not Utils.verify_pwd(pwd.strip(), user_data.user_Password):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        except HTTPException:
            return templates.TemplateResponse("Adminpage.html",
                                              context={"request": request, "error": "Invalid Password"}
                                              , status_code=status.HTTP_409_CONFLICT)

        # After verification we are creating a JWT token to authorize the user for further user task
        access_token = Oauth2.create_access_token(data={"user_email": user_data.user_Email_Id})

        Customer_orders = db.query(models.Customer_login.user_Name, models.Restaurant_table.table_no_Id,
                                   models.User_Orders.food_item_desc, models.User_Orders.person_per_table,
                                   models.User_Orders.order_time, models.Customer_login.user_phone_number).join(
            models.User_Orders,
            models.Customer_login.user_Id == models.User_Orders.user_Id).join(models.Restaurant_table,
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


@router.api_route("/admin_dashborad", status_code=status.HTTP_409_CONFLICT, methods=["GET", "POST"])
async def admin_dashborad(request: Request, db: Session = Depends(get_db)):
    if request.method == "POST":
        user_Id = request.cookies.get("access_token")

        try:
            if not user_Id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        except Token_Exception:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "please login"})

        try:
            user_id_no = Oauth2.get_admin_user(user_Id)
        except Token_Exception:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "please login"})

        Customer_orders = db.query(models.Customer_login.user_Name, models.Restaurant_table.table_no_Id,
                                   models.User_Orders.food_item_desc, models.User_Orders.person_per_table,
                                   models.User_Orders.order_time, models.Customer_login.user_phone_number).join(
            models.User_Orders,
            models.Customer_login.user_Id == models.User_Orders.user_Id).join(models.Restaurant_table,
                                                                              models.User_Orders.user_Id == models.Restaurant_table.user_Id_no)

        return templates.TemplateResponse("Adminpanelpage.html",
                                          context={"request": request, "Customer_data": Customer_orders})






@router.api_route("/billing", status_code=status.HTTP_409_CONFLICT, methods=["GET", "POST"])
async def billing(request: Request, db: Session = Depends(get_db)):
    if request.method == "POST":
        user_Id = request.cookies.get("access_token")
        try:
            if not user_Id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        except Token_Exception:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "please login"})

        try:
            user_id_no = Oauth2.get_admin_user(user_Id)
        except Token_Exception:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "please login"})

        form_data = await request.form()

        user_order_Id = form_data.get("order_ID")
        food_items_placed = form_data.get("food" )
        amount = form_data.get("amount")

        user_order_data = db.query(models.User_Orders).filter(models.User_Orders.order_Id == user_order_Id).first()

        try:
            if not user_order_data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        except HTTPException:
            return templates.TemplateResponse("billdashboard.html", context={"request": request, "msg": "Invalid order_ID"})

        cust_data = db.query(models.Customer_login).filter(models.Customer_login.user_Id == user_order_data.user_Id).first()

        try:
            if not cust_data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        except HTTPException:
            return templates.TemplateResponse("billdashboard.html",
                                              context={"request": request, "msg": "Something went wrong"})

        pdf_content = [
            f"Name: {cust_data.user_Name}",
            f"food details: {food_items_placed}",
            f"Total amount: {amount}",
            f"We hope you like our buffet system",
            f"Please visit us again"
        ]

        make_pdf(pdf_content)

        try:
            send_mail(cust_data.user_Email_Id)
        except Exception:
            return templates.TemplateResponse("billdashboard.html",
                                              context={"request": request, "msg": "Something went wrong contact developer"})

        db.delete(user_order_data)

        db.commit()

        return templates.TemplateResponse("billdashboard.html",context={"request": request, "msg": "Invoice as been send"})


    elif request.method == "GET":
        user_Id = request.cookies.get("access_token")
        try:
            if not user_Id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        except Token_Exception:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "please login"})

        try:
            user_id_no = Oauth2.get_admin_user(user_Id)
        except Token_Exception:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "please login"})

        return templates.TemplateResponse("billdashboard.html", context={"request": request})

    else:
        return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "please login"})





@router.api_route("/add-food-items", status_code=status.HTTP_409_CONFLICT, methods=["GET", "POST"])
async def add_food_items(request: Request, db: Session = Depends(get_db)):
    if request.method == "POST":
        user_Id = request.cookies.get("access_token")
        try:
            if not user_Id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        except Token_Exception:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "please login"})

        try:
            user_id_no = Oauth2.get_admin_user(user_Id)
        except Token_Exception:
            return templates.TemplateResponse("Adminpage.html", context={"request": request, "error": "please login"})

        form_data = await request.form()
        food_name = form_data.get("food_items")
        food_price = form_data.get("food_price")

        add_food_data = models.Food_items(
            food_item=food_name,
            food_price=food_price
        )

        db.add(add_food_data)

        db.commit()

        db.refresh(add_food_data)


@router.get("/test")
async def test(request: Request):
    return  templates.TemplateResponse("adminfooddashboard.html", context={"request": request, "error": "please login"})



# def admin_logout():
#     pass
