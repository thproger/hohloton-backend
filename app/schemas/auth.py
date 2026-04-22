from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime | None = None
    has_avatar: bool


class BusinessRegisterForm(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    geo: str = Field(min_length=2, max_length=200)
    category: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=5, max_length=1000)


class BusinessResponse(BaseModel):
    id: str
    name: str
    geo: str
    category: str
    description: str
    created_at: datetime
    has_photo: bool


class BusinessesListResponse(BaseModel):
    items: list[BusinessResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
