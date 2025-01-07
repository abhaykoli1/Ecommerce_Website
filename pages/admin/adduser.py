import json
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from roles.models.rolesmodel import RolesTable

router = APIRouter()

templates = Jinja2Templates(directory="admintemplates")

@router.get("/admin/adduser", response_class=HTMLResponse)
async def read_index(request: Request):
    userData = request.session.get('userdata')
    roles = RolesTable.objects.all()
    tojson = roles.to_json()
    fromjson = json.loads(tojson)
    return templates.TemplateResponse("adduser.html", {"request": request, "context": userData, "roles": fromjson})