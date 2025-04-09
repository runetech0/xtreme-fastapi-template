from beanie import Document
from pydantic import EmailStr
from typing import Optional
from app.utils import ts_now
from models.user import UserPublic, UserSettings


class User(Document):
    """MongoDB User Model with `user_id` as a UUID string"""

    user_id: str  # Storing UUID as a string
    email: EmailStr
    password: str  # Hashed password
    full_name: Optional[str] = None
    settings: UserSettings = UserSettings()
    is_admin: bool = False  # ✅ New: Flag for admin users
    created_at: int = ts_now()

    class Settings:
        collection = "users"

    def public_version(self) -> UserPublic:
        return UserPublic(
            user_id=self.user_id,
            email=self.email,
            full_name=self.full_name,
            is_admin=self.is_admin,
            created_at=self.created_at,
        )
