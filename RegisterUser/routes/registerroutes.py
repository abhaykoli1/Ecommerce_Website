import jwt
import datetime
from fastapi import APIRouter, HTTPException, Request, Depends, Response
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from pydantic import EmailStr
from fastapi.responses import JSONResponse

from RegisterUser.models.registermodel import RegisterTable, RegisterModel

router = APIRouter()
templates = Jinja2Templates(directory="templates")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key"  # Replace with a secure key
ALGORITHM = "HS256"


# Helper function to hash passwords
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Helper function to verify passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Helper function to create JWT token
def create_jwt_token(user_data: dict) -> str:
    payload = {
        "sub": user_data,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),  # Token valid for 1 day
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Helper function to decode JWT token
def decode_jwt_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/api/v1/registration")
async def add_user(body: RegisterModel):
    if RegisterTable.objects(email=body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        hashed_password = hash_password(body.password)

        new_user = RegisterTable(
            name=body.name,
            email=body.email,
            password=hashed_password,
            phone=body.phone,
        )
        new_user.save()

        # Create JWT token
        token = create_jwt_token({"id": str(new_user.id), "email": new_user.email})

        return {
            "message": "Registration successful",
            "status": True,
            "isAuthenticated": True,
            "token": token,
            "user": {"name": new_user.name, "email": new_user.email},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.delete("/api/v1/users")
async def delete_all_users():
    try:
        deleted_count = RegisterTable.objects.delete()
        return {
            "message": f"Deleted {deleted_count} user(s) successfully",
            "status": True,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# @router.post("/api/v1/login")
# async def login_user(body: dict, response: Response):
#     email_or_phone = body.get("email")  # This field can be either email or phone
#     password = body.get("password")

#     if not email_or_phone or not password:
#         raise HTTPException(status_code=400, detail="Email/Phone and password are required")

#     user = RegisterTable.objects(
#         (RegisterTable.email == email_or_phone) | (RegisterTable.phone == email_or_phone)
#     ).first()

#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid email/phone or password")

#     # Verify password
#     if not verify_password(password, user.password):
#         raise HTTPException(status_code=400, detail="Invalid email/phone or password")

#     # Create JWT token
#     # token = create_jwt_token({"id": str(user.id), "email": user.email})

    

#     return JSONResponse(
#         content={
#             "message": "Login successful",
#             "status": True,
#             "isAuthenticated": True,
#             "user": {"name": user.name, "email": user.email},
#         }
#     )
@router.post("/api/v1/login")
async def login_user(body: dict, response: Response):
    email_or_phone = body.get("email")  # This field can be either email or phone
    password = body.get("password")

    if not email_or_phone or not password:
        raise HTTPException(status_code=400, detail="Email/Phone and password are required")

    # Find user by email or phone
    user = RegisterTable.objects(
        (RegisterTable.email == email_or_phone) | (RegisterTable.phone == email_or_phone)
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email/phone or password")

    # Verify password
    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email/phone or password")

    # Create JWT token
    token = create_jwt_token({"id": str(user.id), "email": user.email})

    # Set token in cookie
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,  # Prevent JavaScript from accessing the cookie
        secure=True,  # Send cookie over HTTPS only
        samesite="strict",  # Prevent cross-site request forgery (CSRF)
        path="/"  # Cookie is accessible across the whole domain
    )

    # Return a response without including the token in the body
    return JSONResponse(
        content={
            "message": "Login successful",
            "status": True,
            "isAuthenticated": True,
            "user": {"name": user.name, "email": user.email},
        }
    )