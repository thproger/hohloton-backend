from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import EmailStr

from app.api.deps import get_current_user_doc
from app.core.security import create_token_pair, hash_password, verify_password
from app.db.mongo import businesses_collection, users_collection
from app.schemas.auth import BusinessRegisterForm, TokenPair, UserLoginRequest, UserResponse
from app.services.user_service import (
    add_update_timestamp,
    build_image_payload,
    ensure_email_unique,
    serialize_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


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
    ensure_email_unique(str(email))

    avatar_bytes = await avatar.read()
    avatar_payload = build_image_payload(avatar, avatar_bytes)
    user_doc = {
        "name": name,
        "email": str(email),
        "password_hash": hash_password(password),
        "avatar": avatar_payload,
        "created_at": datetime.now(timezone.utc),
    }
    result = users_collection.insert_one(user_doc)
    return create_token_pair(subject_id=str(result.inserted_id), subject_type="user")


@router.post("/login/user", response_model=TokenPair)
async def login_user(payload: UserLoginRequest) -> TokenPair:
    user_doc = users_collection.find_one({"email": str(payload.email)})
    if user_doc is None or not verify_password(payload.password, user_doc["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    return create_token_pair(subject_id=str(user_doc["_id"]), subject_type="user")


@router.get("/users/me", response_model=UserResponse)
async def get_current_user(current_user: dict[str, Any] = Depends(get_current_user_doc)) -> UserResponse:
    return serialize_user(current_user)


@router.put("/users/me", response_model=UserResponse)
async def update_current_user(
    current_user: dict[str, Any] = Depends(get_current_user_doc),
    name: str | None = Form(default=None, min_length=2, max_length=100),
    email: EmailStr | None = Form(default=None),
    password: str | None = Form(default=None, min_length=6, max_length=128),
    avatar: UploadFile | None = File(default=None),
) -> UserResponse:
    update_data: dict[str, Any] = {}

    if name is not None:
        update_data["name"] = name
    if email is not None and str(email) != current_user["email"]:
        ensure_email_unique(str(email), current_user["_id"])
        update_data["email"] = str(email)
    if password is not None:
        update_data["password_hash"] = hash_password(password)
    if avatar is not None:
        avatar_bytes = await avatar.read()
        update_data["avatar"] = build_image_payload(avatar, avatar_bytes)

    if not update_data:
        return serialize_user(current_user)

    users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": add_update_timestamp(update_data)},
    )
    updated_user = users_collection.find_one({"_id": current_user["_id"]})
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return serialize_user(updated_user)


@router.post("/register/business", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
async def register_business(
    name: str = Form(..., min_length=2, max_length=120),
    geo: str = Form(..., min_length=2, max_length=200),
    category: str = Form(..., min_length=2, max_length=80),
    description: str = Form(..., min_length=5, max_length=1000),
    photo: UploadFile = File(...),
) -> TokenPair:
    payload = BusinessRegisterForm(
        name=name,
        geo=geo,
        category=category,
        description=description,
    )
    photo_bytes = await photo.read()
    photo_payload = build_image_payload(photo, photo_bytes)
    business_doc = {
        "name": payload.name,
        "geo": payload.geo,
        "category": payload.category,
        "description": payload.description,
        "photo": photo_payload,
        "created_at": datetime.now(timezone.utc),
    }
    result = businesses_collection.insert_one(business_doc)
    return create_token_pair(subject_id=str(result.inserted_id), subject_type="business")
