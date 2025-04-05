import json
import logging
from typing import List
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from Auth.models.usermodel import UserModel, UserTable
from mongoengine import Document, StringField, DateTimeField
from passlib.hash import bcrypt
import uuid
from datetime import datetime, timedelta
import os

from dotenv import load_dotenv
load_dotenv()

# JWT secret key and algorithm (ensure this is secure and stored safely in env variables)
JWT_SECRET_KEY = "your_secret_key_here"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 30  # JWT token expiration time


SMTP_EMAIL = os.getenv("SMTP_EMAIL") 
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
APP_URL = os.getenv("APP_URL") 

# FastAPI Router
router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PendingUserTable(Document):
    name = StringField(required=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    phone = StringField()
    country_code = StringField()
    verification_token = StringField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.utcnow)

class VerificationResponse(BaseModel):
    user_id: str
    email: str
    isAuthentication: bool
    message: str
   
class LoginRequest(BaseModel):
    email: str
    password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
 

def send_verification_email(email: str, token: str):
    # Email content
    subject = "Verify Your Email"
    verification_link = f"{APP_URL}/verify?token={token}"  # Use APP_URL for the link
    body = f"""
    Hello,

    Thank you for registering. Please verify your email by clicking on the link below:

    {verification_link}

    Best regards,
    Your App Team
    """
    
    # Create the email
    msg = MIMEMultipart()
    msg["From"] = SMTP_EMAIL
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification email: {str(e)}"
        )


@router.post("/api/v1/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserModel):
    try:
        # Check if the email already exists in UserTable or PendingUserTable
        if UserTable.objects(email=user.email).first() or PendingUserTable.objects(email=user.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered or pending verification."
            )
        
        # Generate a unique verification token
        verification_token = str(uuid.uuid4())

        # Save the user in the PendingUserTable
        pending_user = PendingUserTable(
            name=user.name,
            email=user.email,
            password=bcrypt.hash(user.password),  # Hashing the password
            phone=user.phone,
            country_code=user.country_code,
            verification_token=verification_token
        )
        pending_user.save()

        # Send the verification email
        send_verification_email(user.email, verification_token)

        return {"message": "User registered successfully. Please check your email for verification."}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/api/v1/verify", status_code=status.HTTP_200_OK)
def verify_user(token: str):
    try:
        pending_user = PendingUserTable.objects(verification_token=token).first()
        if not pending_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token."
            )

        new_user = UserTable(
            name=pending_user.name,
            email=pending_user.email,
            role= "user",
            password=pending_user.password,  
            phone=pending_user.phone,
            country_code=pending_user.country_code
        )
        new_user.save()
        pending_user.delete()
        return {
            "id": str(new_user.id),  
            "email": new_user.email,
            "isLoggedin": True,
            "message": "Email verified successfully. Your account has been created."
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/api/v1/login", status_code=status.HTTP_200_OK)
def login_user(login_request: LoginRequest):

    user = UserTable.objects(email=login_request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with the provided email."
        )

    # Verify the provided password matches the hashed password in the database
    if not verify_password(login_request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password."
        )
  
    return {
        "id": str(user.id),  
        "email": user.email,
        "isLoggedin": True,
        "message": "Login Successfull."
     }

@router.get("/api/v1/user/{user_id}", status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: str):
    """
    Endpoint to retrieve a user by their ID.
    """
    try:
        # Query the user from the database
        user = UserTable.objects(id=user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        # Return the user data
        return {
            "id": str(user.id),
            "name": user.name,
            "role" : user.role,
            "email": user.email,
            "phone": user.phone,
            "country_code": user.country_code,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
        
        
@router.get("/api/v1/users")
async def get_All_Users():
    usersData = []
    findData = UserTable.objects.all()
    for users in findData:
        userTojson = users.to_json()
        fromjson = json.loads(userTojson)
        usersData.append({
            "Users": fromjson,
            # "seo_title": users.seo_title.replace(" ", "-")
        })
    return {
        "message": "All User data",
        "data" : usersData,
        "status": 200
    }
