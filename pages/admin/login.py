from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

router = APIRouter()

templates = Jinja2Templates(directory="admintemplates")

@router.get("/admin/login", response_class=HTMLResponse)
async def read_index(request: Request):
    user = request.session.get('userdata')
    if (user):
        return templates.TemplateResponse("dashboard.html", {"request": request,})
    else: 
        return templates.TemplateResponse("login.html", {"request": request,})
    
@router.post("/admin/login", response_class=HTMLResponse)
async def read_index(request: Request):
    user = request.session.get('userdata')
    if (user):
        return templates.TemplateResponse("dashboard.html", {"request": request,})
    else: 
        return templates.TemplateResponse("login.html", {"request": request,})