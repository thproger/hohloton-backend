from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token
from app.services.user_service import get_user_by_id

bearer_scheme = HTTPBearer()


def get_current_user_doc(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    payload = decode_token(credentials.credentials)
    subject_id = payload.get("sub")
    subject_type = payload.get("kind")
    if not subject_id or subject_type != "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )
    return get_user_by_id(subject_id)
