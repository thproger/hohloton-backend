from __future__ import annotations

import math
from typing import Any

from fastapi import HTTPException, status
from pymongo.collection import Collection

from app.schemas.auth import BusinessResponse, BusinessesListResponse


def serialize_business(business_doc: dict[str, Any]) -> BusinessResponse:
    return BusinessResponse(
        id=str(business_doc["_id"]),
        name=business_doc["name"],
        geo=business_doc["geo"],
        category=business_doc["category"],
        description=business_doc["description"],
        created_at=business_doc["created_at"],
        has_photo=bool(business_doc.get("photo")),
    )


def paginate_businesses(
    *,
    collection: Collection[Any],
    query: dict[str, Any],
    page: int,
    page_size: int,
) -> BusinessesListResponse:
    if page < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="page_size must be between 1 and 100")

    total = int(collection.count_documents(query))
    total_pages = max(1, math.ceil(total / page_size)) if total else 1
    skip = (page - 1) * page_size

    cursor = (
        collection.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(page_size)
    )
    items = [serialize_business(doc) for doc in cursor]
    return BusinessesListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )
