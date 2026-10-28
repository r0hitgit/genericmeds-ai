from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)


def verify_admin_key(api_key: str = Security(api_key_header)) -> bool:
    """
    Verifies that the incoming request has a valid administrative API key.
    Used to protect administrative data ingestion endpoints.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin API key is missing. Provide 'X-Admin-Key' header.",
        )
    if api_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Admin API key.",
        )
    return True
