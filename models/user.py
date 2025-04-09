from pydantic import EmailStr, BaseModel
from typing import Optional
from datetime import datetime


class UserSettings(BaseModel):
    """User settings model"""


class UserPublic(BaseModel):
    """Public user model for admin dashboard (without `tweets`)"""

    user_id: str
    email: EmailStr
    full_name: Optional[str]
    is_admin: bool
    created_at: int


class Notification(BaseModel):
    id: int
    message: str
    read: bool
    created_at: datetime


class ActivityLog(BaseModel):
    action: str
    timestamp: datetime


class DeleteUserRequest(BaseModel):
    confirm: bool
