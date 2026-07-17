from datetime import datetime

from pydantic import BaseModel, EmailStr


class AdminUserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserStatusUpdate(BaseModel):
    is_active: bool


class PlatformStats(BaseModel):
    total_users: int
    active_users: int
    total_contacts: int
    total_calls: int