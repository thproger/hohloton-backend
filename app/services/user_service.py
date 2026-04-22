from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.binary import Binary
from fastapi import HTTPException, UploadFile, status

from app.db.mongo import users_collection
from app.schemas.auth import UserResponse


def build_image_payload(file: UploadFile | None, file_bytes: bytes | None) -> dict[str, Any] | None:
    if file is None:
        return None
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file is empty",
        )
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "data": Binary(file_bytes),
    }


def serialize_user(user_doc: dict[str, Any]) -> UserResponse:
    return UserResponse(
        id=str(user_doc["_id"]),
        name=user_doc["name"],
        email=user_doc["email"],
        created_at=user_doc["created_at"],
        updated_at=user_doc.get("updated_at"),
        has_avatar=bool(user_doc.get("avatar")),
    )


def get_user_by_id(user_id: str) -> dict[str, Any]:
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )
    user_doc = users_collection.find_one({"_id": ObjectId(user_id)})
    if user_doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user_doc


def ensure_email_unique(email: str, current_user_id: ObjectId | None = None) -> None:
    existing_user = users_collection.find_one({"email": email})
    if existing_user is None:
        return
    if current_user_id is not None and existing_user["_id"] == current_user_id:
        return
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User with this email already exists",
    )


def add_update_timestamp(update_data: dict[str, Any]) -> dict[str, Any]:
    update_data["updated_at"] = datetime.now(timezone.utc)
    return update_data
