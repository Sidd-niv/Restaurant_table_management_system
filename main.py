from fastapi import FastAPI, status,  Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import models
from database_con import engine
from routers import users, adminUser
from fastapi.middleware.cors import CORSMiddleware

# Defining the instance of fastapi
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Defining the template object for jinja2Templating to access/ render the html templates
templates = Jinja2Templates(directory="templates/")

# mounting the static files, through which fastapi can access the css and images files
app.mount("/static", StaticFiles(directory="static/"), name="static")

# this will the uncreated tables which is going to be used in application
models.Base.metadata.create_all(bind=engine)

# Default page api
@app.get("/", status_code=status.HTTP_200_OK)
def home(request: Request):
    return templates.TemplateResponse("Home_page.html", context={"request": request})

# Through this fastapi instances will find the required routes
app.include_router(users.router)
app.include_router(adminUser.router)





