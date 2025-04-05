from mongoengine import Document, StringField, IntField, FloatField, DateTimeField
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductTable(Document):
    image = StringField(required=True)
    name = StringField(required=True)
    description = StringField(required=True)
    category = StringField(required=True)
    brand = StringField(required=True)
    price = FloatField(required=True)
    sale_price = FloatField(required=False)
    total_stock = IntField(required=True)
    average_review = FloatField(required=False)
    # created_at = DateTimeField(default=datetime.utcnow)
    # updated_at = DateTimeField(default=datetime.utcnow)
    meta = {'collection': 'products'} 
    

class ProductModel(BaseModel):
    image: str
    name: str
    description: str
    category: str
    brand: str
    price: float
    sale_price: Optional[float] = None
    total_stock: int
    average_review: Optional[float] = None
    # created_at: Optional[datetime] = None
    # updated_at: Optional[datetime] = None