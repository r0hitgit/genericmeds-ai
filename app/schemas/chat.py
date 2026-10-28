from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.medicine import MedicineProductSummary
from app.schemas.pricing import PriceComparisonResponse


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user', 'assistant', or 'system'")
    content: str


class ChatExtractedEntity(BaseModel):
    medicine_name: Optional[str] = None
    active_ingredients: Optional[List[str]] = None
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    intent: str = Field("search", description="search, compare, composition_explain, alternative, emergency, general")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User's query")
    language: Optional[str] = Field("en", description="'en' for English or 'hi' for Hindi")
    conversation_history: Optional[List[ChatMessage]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    extracted_entities: Optional[ChatExtractedEntity] = None
    structured_medicines: Optional[List[MedicineProductSummary]] = None
    structured_comparison: Optional[PriceComparisonResponse] = None
    warnings: List[str] = []
    sources: List[Dict[str, Any]] = []
    follow_up_questions: List[str] = []
    disclaimer: str
