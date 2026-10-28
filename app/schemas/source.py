from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DataSourceOut(BaseModel):
    id: int
    source_name: str
    source_url: str
    source_type: str
    last_checked_at: Optional[datetime] = None
    last_successful_sync_at: Optional[datetime] = None
    data_status: str
    medicine_count: Optional[int] = 0

    class Config:
        from_attributes = True


class AdminImportReport(BaseModel):
    source_name: str
    source_url: Optional[str] = None
    records_processed: int
    records_created: int
    records_updated: int
    validation_errors: List[str] = []
    status: str = Field(..., description="'success', 'partial_success', 'failed'")
