from fastapi import FastAPI, status, HTTPException, Depends, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import Oauth2
import Utils
import models
from database_con import engine, get_db

app = FastAPI()

templates = Jinja2Templates(directory="templates/")
app.mount("/static", StaticFiles(directory="static/"), name="static")

models.Base.metadata.create_all(bind=engine)


@app.get("/", status_code=status.HTTP_200_OK)
def home(request: Request):
    return templates.TemplateResponse("Home_page.html", context={"request": request})


@app.get("/user_register")
async def user_register_page(request: Request):
    return templates.TemplateResponse("Registration_page.html", context={"request": request})


@app.post("/register", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def user_register(request: Request, name: str = Form(...), email_id: str = Form(...), phone: int = Form(...),
                        pwd: str = Form(...), db: Session = Depends(get_db)):

    new_pwd = Utils.get_Hash_pwd(pwd)

    new_user = models.Customer_login(user_Name=name,
                                     user_Email_Id=email_id,
                                     user_Password=new_pwd,
                                     user_phone_number=phone,
                                     user_type="Nrl")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return  templates.TemplateResponse("login_page.html", context={"request": request})


@app.get("/user_login", status_code=status.HTTP_200_OK)
def login_page(request: Request):
    return templates.TemplateResponse("login_page.html", context={"request": request})


@app.post("/login", response_class=HTMLResponse)
def login( response: Response, request: Request,email_id: str = Form(...), pwd: str = Form(...), db: Session = Depends(get_db)):
    user_data = db.query(models.Customer_login).filter(
        models.Customer_login.user_Email_Id == email_id).first()
    try:
        if not user_data:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except HTTPException:
        return templates.TemplateResponse("login_page.html", context={"request": request, "error": "Invalid Email or User Not found"})
    try:
        if not Utils.verify_pwd(pwd, user_data.user_Password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except HTTPException:
        return templates.TemplateResponse("login_page.html", context={"request": request, "error": "Invalid Password"})

    access_token = Oauth2.create_access_token(data={"user_Id": user_data.user_Id})
    response = templates.TemplateResponse("userdashbroad.html", context={"request": request})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response



@app.get("/user_Dashbroad", status_code=status.HTTP_200_OK)
def user_Dashbroad(request: Request):
    user_Id = request.cookies.get("access_token")
    try:
        Oauth2.get_current_user(user_Id)
    except HTTPException:
        return templates.TemplateResponse("login_page.html", context={"request": request, "error": "Please login"})

    return templates.TemplateResponse("userdashbroad.html", context={"request": request, "error": "success"})




