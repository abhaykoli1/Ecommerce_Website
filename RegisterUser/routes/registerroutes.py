import jwt
import datetime
from fastapi import APIRouter, HTTPException, Request, Depends
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


@router.post("/api/v1/login")
async def login_user(body: RegisterModel):
    # Check if user exists
    user = RegisterTable.objects(email=body.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Verify password
    if not verify_password(body.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Create JWT token
    token = create_jwt_token({"id": str(user.id), "email": user.email})

    return {
        "message": "Login successful",
        "status": True,
        "isAuthenticated": True,
        "token": token,
        "user": {"name": user.name, "email": user.email},
    }


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Middleware to check authentication
@router.get("/api/v1/auth-check")
async def auth_check(token: str):
    try:
        user_data = decode_jwt_token(token)
        return {"isAuthenticated": True, "user": user_data}
    except HTTPException as e:
        return {"isAuthenticated": False, "user": None}
