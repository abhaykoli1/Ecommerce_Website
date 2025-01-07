import json
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from services.models.serviocemodels import ServiceTable

router = APIRouter()

templates = Jinja2Templates(directory="admintemplates")

@router.get("/admin/addservice", response_class=HTMLResponse)
async def read_index(request: Request):
    userData = request.session.get('userdata') 
    services = ServiceTable.objects.all()
    tojson = services.to_json()
    fromjson = json.loads(tojson)
    return templates.TemplateResponse("addservice.html", {"request": request, "context": userData, "serviceList": fromjson})