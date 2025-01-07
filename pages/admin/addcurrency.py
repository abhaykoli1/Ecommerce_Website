import json
from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from currency.models.currencymodelo import CurrencyTable

router = APIRouter()

templates = Jinja2Templates(directory="admintemplates")

@router.get("/admin/addcurrency", response_class=HTMLResponse)
async def read_index(request: Request):
    userData = request.session.get('userdata')
    data = CurrencyTable.objects.all()
    tojson = data.to_json()
    fromjson = json.loads(tojson)
    return templates.TemplateResponse("addcurrency.html", {"request": request, "context":userData, "currencyList": fromjson})