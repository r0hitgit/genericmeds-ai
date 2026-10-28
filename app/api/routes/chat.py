from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.ai.llm_service import LLMService

router = APIRouter(prefix="/api/v1/chat", tags=["AI Chat Assistant"])
llm_service = LLMService()


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_genericmeds_ai(
    req: ChatRequest,
    db: Session = Depends(get_db),
):
    """
    Intelligent medicine discovery assistant.
    Accepts user inquiries, extracts structured entities (medicine name, ingredients, strength, form),
    retrieves verified records from the catalogue, and provides grounded explanations in simple English or Hindi.
    """
    return await llm_service.process_chat(
        db=db,
        message=req.message,
        language=req.language or "en",
        conversation_history=req.conversation_history,
    )
