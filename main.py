from fastapi import FastAPI
import uvicorn
import os
from dotenv import load_dotenv
from mongoengine import connect
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from RegisterUser.routes import registerroutes

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in .env file")

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file")

# Connect to MongoDB


connect('Ecommerce', host="mongodb+srv://abhaykoli214:Abhaykoli0@bikerental.ocb4d.mongodb.net/Ecommerce")
# connect('UAAWebsite', host="mongodb+srv://avbigbuddy:nZ4ATPTwJjzYnm20@cluster0.wplpkxz.mongodb.net/UAAWebsite")

# Initialize FastAPI app
app = FastAPI()

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Session Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=604800,
    session_cookie="your_session_cookie",
)

# Include routes
app.include_router(registerroutes.router, tags=["Registration"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
