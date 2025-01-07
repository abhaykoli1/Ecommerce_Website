from mongoengine import Document, StringField ,DateTimeField
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# MongoDB Model
class RegisterTable(Document):
    name = StringField(required=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    phone = StringField(required=False)
    # country_code = StringField(required=False)
    created_at = DateTimeField(default=datetime.utcnow)

# Pydantic Model
class RegisterModel(BaseModel):
    name: str
    email: str  # Use EmailStr for stricter validation
    password: str
    phone: Optional[str] = None  # Optional fields should use Optional
    country_code: Optional[str] = None
