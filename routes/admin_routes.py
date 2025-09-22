from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select

from app.auth_service import create_access_token, get_admin_user, verify_password
from app.logs_config import get_logger
from db_handles.admin_settings import AdminSettings
from db_handles.session import async_session
from db_handles.user import User
from models.admin import Log, Role
from models.admin_settings import AdminSettingsOutput, AdminSettingsUpdate
from models.auth import UserLogin
from models.user import UserPublic

logger = get_logger()


admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@admin_router.post("/login")
async def admin_login(user_data: UserLogin) -> dict[str, str]:
    """Authenticate admin and return JWT token"""
    user = await User.get_by_email(user_data.email)
    if (
        not user
        or not verify_password(user_data.password, user.hashed_password)
        or not user.is_admin
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token: str = create_access_token(data={"user_id": user.id, "is_admin": True})
    return {"access_token": token, "token_type": "bearer"}


@admin_router.get("/settings/", response_model=AdminSettingsOutput)
async def get_admin_settings(
    admin: User = Depends(get_admin_user),
) -> AdminSettingsOutput:
    """Retrieve global admin settings"""
    logger.debug("/settings was called to get the admin settings ...")
    settings = await AdminSettings.get_settings()

    assert isinstance(settings, AdminSettings), (
        "Admin settings not found even though it should be"
    )

    return settings.output_version()


@admin_router.put("/settings/")
async def update_admin_settings(
    new_settings: AdminSettingsUpdate, admin: User = Depends(get_admin_user)
) -> dict[str, str]:
    """Update global admin settings"""

    settings = await AdminSettings.get_settings()

    assert isinstance(settings, AdminSettings), (
        "Admin settings not found even though it should be"
    )

    await settings.update_settings(**new_settings.model_dump())

    logger.debug(f"Updating admin settings to new settings: {new_settings}")

    logger.debug(f"Admin settings updated: {settings}")

    return {"message": "Admin settings updated successfully"}


@admin_router.get("/users/")
async def get_all_users(
    count: int = Query(10, gt=0, le=100),  # Limit: max 100 users per request
    cursor: int | None = None,  # Use created_at as cursor (timestamp int)
    admin: User = Depends(get_admin_user),
) -> dict[str, Any]:
    """Retrieve paginated list of all registered users (Admin-only)"""

    # Build base query: order by created_at descending (newest first)
    stmt = select(User).order_by(User.created_at.desc()).limit(count)

    # If cursor is provided, fetch users with created_at < cursor
    if cursor:
        stmt = stmt.where(User.created_at < cursor)

    async with async_session() as session:
        result = await session.execute(stmt)
        users_db = result.scalars().all()

    # Convert to public version
    users = [user.public_version() for user in users_db]

    # Get next cursor (last user's created_at)
    next_cursor = users_db[-1].created_at if users_db else None

    return {"users": users, "next_cursor": next_cursor}


@admin_router.get("/users/{user_id}", response_model=UserPublic)
async def get_user(user_id: str, admin: User = Depends(get_admin_user)) -> UserPublic:
    user = await User.get_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.public_version()


@admin_router.put("/users/{user_id}", response_model=UserPublic)
async def update_user(
    user_id: str, admin: User = Depends(get_admin_user)
) -> UserPublic:
    user = await User.get_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # await user.update_settings(**new_settings.model_dump())
    return user.public_version()


@admin_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, admin: User = Depends(get_admin_user)) -> None:
    user = await User.get_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete()
    return


# 2. Platform Stats (/admin/stats)
@admin_router.get("/stats", response_model=dict)
async def get_platform_stats(admin: User = Depends(get_admin_user)) -> dict[str, int]:
    user_count = await User.get_count()
    return {
        "user_count": user_count,
        "active_users": await User.get_count(),
    }


# 3. System-wide Logs (/admin/logs)
@admin_router.get("/logs", response_model=list[Log])
async def get_logs(admin: User = Depends(get_admin_user)) -> list[Log]:
    return []


# 4. Role/Permission Management (/admin/roles)
@admin_router.get("/roles", response_model=list[Role])
async def get_roles(admin: User = Depends(get_admin_user)) -> list[Role]:
    return []


# @admin_router.post("/roles", response_model=Role)
# async def create_role(role: Role, admin: User = Depends(get_admin_user)) -> Role:
#     # Check if the role already exists
#     if any(r["role"] == role.role for r in fake_roles_db):
#         raise HTTPException(status_code=400, detail="Role already exists")
#     fake_roles_db.append(role.dict())
#     return role


# @admin_router.put("/roles/{role_name}", response_model=Role)
# async def update_role(
#     role_name: str, role: Role, admin: User = Depends(get_admin_user)
# ) -> Role:
#     for i, r in enumerate(fake_roles_db):
#         if r["role"] == role_name:
#             fake_roles_db[i] = role.dict()
#             return role
#     raise HTTPException(status_code=404, detail="Role not found")


# @admin_router.delete("/roles/{role_name}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_role(role_name: str, admin: User = Depends(get_admin_user)) -> None:
#     role = next((r for r in fake_roles_db if r["role"] == role_name), None)
#     if not role:
#         raise HTTPException(status_code=404, detail="Role not found")
#     fake_roles_db.remove(role)
#     return {"message": f"Role {role_name} deleted successfully"}


# # 5. App-level Configuration (/admin/config)
# @admin_router.get("/config", response_model=Config)
# async def get_config(admin: User = Depends(get_admin_user)) -> Config:
#     return fake_config_db


# @admin_router.put("/config", response_model=Config)
# async def update_config(
#     config: Config, admin: User = Depends(get_admin_user)
# ) -> Config:
#     fake_config_db.update(config.dict())
#     return fake_config_db
