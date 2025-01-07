import json
from bson import ObjectId
from datetime import datetime
from fastapi import FastAPI, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from client.models.clientmodel import ClientTable
from order.models.ordermodel import OrderTable
from services.models.serviocemodels import ServiceTable
from user.models.usermodel import UserTable

router = APIRouter()

templates = Jinja2Templates(directory="admintemplates")

@router.get("/admin/orderlist", response_class=HTMLResponse)
async def read_index(request: Request):
    data = []
    user = request.session.get('userdata')
    if(user['role']['v'] == 4):

        allorder = OrderTable.objects.all()
        for order in allorder:
            finduser = UserTable.objects.get(id=ObjectId(str(order.userId)))
            touser = finduser.to_json()
            fromuserjson = json.loads(touser)
            pendingamount = order.totalorderamount - order.clientpaidAmount
            ordertojson = order.to_json()
            orderfromjson = json.loads(ordertojson)
            clintdata = ClientTable.objects.get(id=ObjectId(str(order.clintId)))
            servicedata = ServiceTable.objects.get(id=ObjectId(str(order.serviceId)))
            data.append({
                'user': fromuserjson,
                'pendingamount': pendingamount,
                'order': orderfromjson,
                'clientName': clintdata.name,
                'service': servicedata.title,
                "pendingamount": order.totalorderamount - order.clientpaidAmount
            })
    else:
        allorder = OrderTable.objects(userId=str(user['data']['_id']['\u0024oid'])).all()
        for order in allorder:
            finduser = UserTable.objects.get(id=ObjectId(str(order.userId)))
            touser = finduser.to_json()
            fromuserjson = json.loads(touser)
            pendingamount = order.totalorderamount - order.clientpaidAmount
            ordertojson = order.to_json()
            orderfromjson = json.loads(ordertojson)
            clintdata = ClientTable.objects.get(id=ObjectId(str(order.clintId)))
            servicedata = ServiceTable.objects.get(id=ObjectId(str(order.serviceId)))
            data.append({
                'user': fromuserjson,
                'pendingamount': pendingamount,
                'order': orderfromjson,
                'clientName': clintdata.name,
                'service': servicedata.title,
                "pendingamount": order.totalorderamount - order.clientpaidAmount
            })
    
        
    return templates.TemplateResponse("orderslist.html", {"request": request, "context":user, "orderes" : data, "userdata": user})