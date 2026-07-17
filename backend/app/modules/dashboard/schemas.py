from datetime import datetime

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_contacts: int
    total_calls: int
    calls_completed: int
    calls_failed_or_missed: int
    total_call_minutes: float


class RecentCallOut(BaseModel):
    id: int
    contact_name: str
    direction: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True