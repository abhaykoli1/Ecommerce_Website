from datetime import date, datetime
import json

from fastapi import FastAPI ,APIRouter, HTTPException
from products.models.productsmodel import ProductModel, ProductTable

router = APIRouter()

# Add Service Endpoint
@router.post("/api/v1/add-new-product")
async def add_product(body: ProductModel):
    try:
        save_data = ProductTable(
            image=body.image,
            name=body.name,
            description=body.description,
            category=body.category,
            brand=body.brand,
            price=body.price,
            sale_price=body.sale_price,
            total_stock=body.total_stock,
            average_review=body.average_review,
        )
        save_data.save()  

        return {
            "message": "product added successfully",
            "status": 201
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while adding the service")
    
    

@router.get("/api/v1/get-allService")
async def getAllService():
    productData = []
    findData = ProductTable.objects.all()
    for product in findData:
        serviceTojson = product.to_json()
        fromjson = json.loads(serviceTojson)
        productData.append({
            "details": fromjson,
        })
    return {
        "message": "All Product data",
        "data" : productData,
        "status": 200
    }
    
    