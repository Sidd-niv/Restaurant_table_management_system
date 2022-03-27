from fastapi import FastAPI, status, HTTPException, Depends, Request, Form, Response
# from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import models
from database_con import engine
from routers import users, adminUser
app = FastAPI()

templates = Jinja2Templates(directory="templates/")
app.mount("/static", StaticFiles(directory="static/"), name="static")

models.Base.metadata.create_all(bind=engine)


@app.get("/", status_code=status.HTTP_200_OK)
def home(request: Request):
    return templates.TemplateResponse("Home_page.html", context={"request": request})


app.include_router(users.router)
app.include_router(adminUser.router)





