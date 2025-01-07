from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

router = APIRouter()

templates = Jinja2Templates(directory="admintemplates")

@router.get("/admin/addclient", response_class=HTMLResponse)
async def read_index(request: Request):
    userData = request.session.get('userdata')
    return templates.TemplateResponse("addclient.html", {"request": request, "context": userData})