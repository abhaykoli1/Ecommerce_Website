import json
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from client.models.clientmodel import ClientTable

router = APIRouter()

templates = Jinja2Templates(directory="admintemplates")

@router.get("/admin/clientList", response_class=HTMLResponse)
async def read_index(request: Request):
    user = request.session.get('userdata')
    data = ClientTable.objects.all()
    if user['role']['name'] != 'Admin':
        data = ClientTable.objects(userid=str(user['data']['_id']['\u0024oid'])).all()
    tojson = data.to_json()
    fromjson = json.loads(tojson)
    return templates.TemplateResponse("clientlist.html", {"request": request, "context": user, "clientList": fromjson})
    
