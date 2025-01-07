import json
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from client.models.clientmodel import ClientTable
from currency.models.currencymodelo import CurrencyTable
from services.models.serviocemodels import ServiceTable
from user.models.usermodel import UserTable

router = APIRouter()

templates = Jinja2Templates(directory="admintemplates")

@router.get("/admin/addorder", response_class=HTMLResponse)
async def read_index(request: Request):
    currencytable = CurrencyTable.objects.all()
    tojson = currencytable.to_json()
    fromjson = json.loads(tojson)
    userData = request.session.get('userdata')
    clientList = ClientTable.objects.all()
    if userData['role']['name'] != 'Admin':
        clientList = ClientTable.objects(userid=str(userData['data']['_id']['\u0024oid'])).all()
    clientlistjson = clientList.to_json()
    fromClientJson = json.loads(clientlistjson)
    serviceList = ServiceTable.objects.all()
    serviceTojson = serviceList.to_json()
    serviceFromJson = json.loads(serviceTojson)
    return templates.TemplateResponse("addorder.html", {"request": request, "context":userData, "currency": fromjson, "clientsList": fromClientJson, "serviceList": serviceFromJson})