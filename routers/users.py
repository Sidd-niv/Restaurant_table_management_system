from fastapi import Request, status, HTTPException, Form, Depends, Response, APIRouter
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import Oauth2
import Utils
import models
import schemas
from database_con import get_db
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

router = APIRouter(
    tags=["User"]
)

templates = Jinja2Templates(directory="templates/")
router.mount("/static", StaticFiles(directory="static/"), name="static")

@router.get("/user_register")
async def user_register_page(request: Request):
    return templates.TemplateResponse("Registration_page.html", context={"request": request})


@router.post("/register", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def user_register(request: Request, name: str = Form(...), email_id: str = Form(...), phone: int = Form(...),
                        pwd: str = Form(...), db: Session = Depends(get_db)):

    new_pwd = Utils.get_Hash_pwd(pwd.strip())

    new_user = models.Customer_login(user_Name=name.strip(),
                                     user_Email_Id=email_id.strip(),
                                     user_Password=new_pwd,
                                     user_phone_number=phone,
                                     user_type="Nrl")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return  templates.TemplateResponse("login_page.html", context={"request": request})


@router.get("/user_login", status_code=status.HTTP_200_OK)
def login_page(request: Request):
    return templates.TemplateResponse("login_page.html", context={"request": request})


@router.post("/login", response_class=HTMLResponse)
def login( response: Response, request: Request,email_id: str = Form(...), pwd: str = Form(...), db: Session = Depends(get_db)):
    user_data = db.query(models.Customer_login).filter(
        models.Customer_login.user_Email_Id == email_id.strip()).first()
    try:
        if not user_data:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except HTTPException:
        return templates.TemplateResponse("login_page.html", context={"request": request, "error": "Invalid Email or User Not found"}
                                          , status_code=status.HTTP_403_FORBIDDEN)

    try:
        if not Utils.verify_pwd(pwd.strip(), user_data.user_Password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except HTTPException:
        return templates.TemplateResponse("login_page.html", context={"request": request, "error": "Invalid Password"}
                                          , status_code=status.HTTP_409_CONFLICT)

    access_token = Oauth2.create_access_token(data={"user_Id": user_data.user_Id})
    user_name = user_data.user_Name
    response = templates.TemplateResponse("userdashbroad.html", context={"request": request, "user": user_name})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response



@router.api_route("/user_Dashbroad", status_code=status.HTTP_409_CONFLICT, methods=["GET", "POST"])
def user_Dashbroad(response: Response, request: Request, table_no : str = Form(...), item: str = Form(...),
                   user_time: str = Form(...), db: Session = Depends(get_db)):
    if request.method == "POST":
        user_Id = request.cookies.get("access_token")
        try:
            user_id_no = Oauth2.get_current_user(user_Id)
        except HTTPException:
            return templates.TemplateResponse("login_page.html", context={"request": request, "error": "Please login"},
                                              status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)

        print(table_no, item, user_time)
        user_name = db.query(models.Customer_login).filter(models.Customer_login.user_Id == user_id_no["id"]).first()
        print(user_name.user_Name)
        return templates.TemplateResponse("userdashbroad.html", context={"request": request, "error": "success"})


    return templates.TemplateResponse("userdashbroad.html", context={"request": request, "error": "success"})


