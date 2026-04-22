import os
from datetime import datetime, timedelta, timezone
from typing import Any

from bson.binary import Binary
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

router = APIRouter(prefix="/auth", tags=["auth"])

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://vadimvrachenko_db_user:<db_password>@cluster0.47ucd3e.mongodb.net/?appName=Cluster0")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "hohloton")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

mongo_client: MongoClient[Any] = MongoClient(MONGODB_URL)
db: Database[Any] = mongo_client[MONGODB_DB_NAME]
users_collection: Collection[Any] = db["users"]
businesses_collection: Collection[Any] = db["businesses"]


class BusinessRegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    geo: str = Field(min_length=2, max_length=200)
    category: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=5, max_length=1000)
    photo: str | None = Field(default=None, max_length=500)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


def create_token(payload: dict[str, Any], expires_delta: timedelta) -> str:
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_token_pair(subject_id: str, subject_type: str) -> TokenPair:
    access_token = create_token(
        {"sub": subject_id, "kind": subject_type},
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_token(
        {"sub": subject_id, "kind": subject_type, "scope": "refresh"},
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "Auth service is running"}


@router.post("/register/user", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register_user(
    name: str = Form(..., min_length=2, max_length=100),
    email: EmailStr = Form(...),
    password: str = Form(..., min_length=6, max_length=128),
    avatar: UploadFile = File(...),
) -> TokenPair:
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    avatar_bytes = await avatar.read()
    if not avatar_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Avatar file is empty",
        )

    user_doc = {
        "name": name,
        "email": email,
        "password_hash": hash_password(password),
        "avatar": {
            "filename": avatar.filename,
            "content_type": avatar.content_type,
            "data": Binary(avatar_bytes),
        },
        "created_at": datetime.now(timezone.utc),
    }
    result = users_collection.insert_one(user_doc)
    return create_token_pair(subject_id=str(result.inserted_id), subject_type="user")


@router.post(
    "/register/business",
    response_model=TokenPair,
    status_code=status.HTTP_201_CREATED,
)
async def register_business(payload: BusinessRegisterRequest) -> TokenPair:
    business_doc = {
        "name": payload.name,
        "geo": payload.geo,
        "category": payload.category,
        "description": payload.description,
        "photo": payload.photo,
        "created_at": datetime.now(timezone.utc),
    }
    result = businesses_collection.insert_one(business_doc)
    return create_token_pair(subject_id=str(result.inserted_id), subject_type="business")