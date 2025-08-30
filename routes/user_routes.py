import os
from typing import Dict
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.auth_service import get_current_user, hash_password, verify_password
from app.types import GeneralDict
from db_handles.user import User
from models.user import (
    ActivityLog,
    DeleteUserRequest,
    Notification,
    UserPublic,
    UserSettings,
)

user_router: APIRouter = APIRouter(prefix="/user", tags=["User"])


@user_router.get("/settings", response_model=UserSettings)
async def get_settings(user: User = Depends(get_current_user)) -> UserSettings:
    """Retrieve user settings"""
    await user.get_settings()
    return UserSettings()


@user_router.put("/settings", status_code=status.HTTP_200_OK)
async def update_settings(
    new_settings: UserSettings, user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Update user settings"""
    await user.update_settings(**new_settings.model_dump())
    return {"message": "Settings updated successfully"}


@user_router.get("/profile", response_model=UserPublic)
async def get_profile(user: User = Depends(get_current_user)) -> UserPublic:
    """Get user profile (full name & email)"""
    return user.public_version()


@user_router.put("/change-password/", status_code=status.HTTP_200_OK)
async def change_password(
    old_password: str, new_password: str, user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Change user password"""
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    user.hashed_password = hash_password(new_password)
    await user.update_settings(hashed_password=user.hashed_password)
    return {"message": "Password updated successfully"}


# Define the directory where profile pictures will be stored
AVATAR_DIR = "avatars"
os.makedirs(AVATAR_DIR, exist_ok=True)


# 1. Avatar Upload/Change
@user_router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...)) -> GeneralDict:
    if not file.filename:
        raise HTTPException(400, "Missing the filename of on avatar!")
    file_extension = file.filename.split(".")[-1]
    if file_extension not in ["jpg", "jpeg", "png"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only jpg, jpeg, and png are allowed.",
        )

    avatar_id = str(uuid4())
    avatar_path = os.path.join(AVATAR_DIR, f"{avatar_id}.{file_extension}")

    with open(avatar_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return {"message": "Profile picture uploaded successfully", "avatar_id": avatar_id}


# 2. User Notifications
@user_router.get("/notifications", response_model=list[Notification])
async def get_notifications() -> list[Notification]:
    return []


@user_router.post("/notifications/{notification_id}/mark-as-read")
async def mark_notification_as_read(notification_id: int) -> GeneralDict:
    # Find notification by ID
    return {"message": "Notification marked as read"}


# 3. User Activity Log
@user_router.get("/activity-log", response_model=list[ActivityLog])
async def get_activity_log() -> list[ActivityLog]:
    return []


# 4. Account Deletion/Deactivation
@user_router.post("/delete")
async def delete_account(request: DeleteUserRequest) -> GeneralDict:
    if not request.confirm:
        raise HTTPException(
            status_code=400, detail="Account deletion confirmation is required."
        )

    # Here, you would implement the actual deletion logic, e.g., deleting the user from the database
    return {"message": "Your account has been deactivated successfully."}
