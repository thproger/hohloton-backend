from fastapi import APIRouter, HTTPException, status

from google.genai import types

from app.core.config import GEMINI_MODEL
from app.db.mongo import businesses_collection
from app.schemas.ai import AIAskRequest, AIAskResponse
from app.services.business_service import businesses_to_csv_rows
from app.services.ai import client

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status")
async def ai_status() -> dict[str, bool]:
    return {"client_available": client is not None}


@router.post("/ask", response_model=AIAskResponse)
async def ask_ai(payload: AIAskRequest) -> AIAskResponse:
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI client is not configured. Set GEMINI_API_KEY",
        )

    businesses = list(
        # businesses_collection.find(
        #     {},
        #     {"name": 1, "geo": 1, "category": 1},
        # )
    )
    # csv_data = businesses_to_csv_rows(businesses)
    composed_prompt = (
        f"{payload.text}\n\n"
        "CSV with all businesses (category,name,geo):\n"
        # f"{csv_data}"
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=(
                "Ти помічник каталогу бізнесів. Надавай рекомендації по Миколаєву. Вибирай здебільшого маловідомі сервіси"
            ),
        ),
        contents=composed_prompt,
    )
    return AIAskResponse(answer=response.text or "")
