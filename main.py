from fastapi import FastAPI
import uvicorn
import os
from dotenv import load_dotenv
from mongoengine import connect
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from Auth.routes import userroutes
from imageUpload import imageuploadroutes
from products.routes import productsroutes

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in .env file")

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file")


connect('Ecommerce', host="mongodb+srv://abhaykoli214:Abhaykoli0@bikerental.ocb4d.mongodb.net/Ecommerce")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,  
    allow_methods=["GET", "POST", "PATCH", "DELETE", "PUT"],   
    allow_headers=["Content-Type", "Authorization", "Cache-Control", "Expires", "Pragma"],  # Allowed headers

)

app.include_router(userroutes.router, tags=["Auth"])
app.include_router(productsroutes.router, tags=["products"])
app.include_router(imageuploadroutes.router, tags=["image Upload"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
