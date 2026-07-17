from datetime import date

from pydantic import BaseModel


class CallVolumePoint(BaseModel):
    day: date
    total_calls: int
    completed_calls: int


class StatusBreakdown(BaseModel):
    status: str
    count: int


class DirectionBreakdown(BaseModel):
    direction: str
    count: int