from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Any, Optional

# from models.admin import Log
from models.user import UserPublic
from models.auth import UserLogin
from app.auth_service import verify_password
from fastapi import APIRouter, Depends
from typing import Dict
from app.auth_service import get_admin_user, create_access_token
from app.db.user import User
from app.db.admin_settings import AdminSettings
from app.logger import logger

admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@admin_router.post("/login")
async def admin_login(user_data: UserLogin) -> Dict[str, str]:
    """Authenticate admin and return JWT token"""
    user: Optional[User] = await User.find_one(
        User.email == user_data.email, projection_model=User
    )
    if (
        not user
        or not verify_password(user_data.password, user.password)
        or not user.is_admin
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token: str = create_access_token(data={"user_id": user.user_id, "is_admin": True})
    return {"access_token": token, "token_type": "bearer"}


@admin_router.get("/settings/", response_model=AdminSettings)
async def get_admin_settings(admin: User = Depends(get_admin_user)) -> AdminSettings:
    """Retrieve global admin settings"""
    logger.debug("/settings was called to get the admin settings ...")
    settings = await AdminSettings.find_one(projection_model=AdminSettings)

    # ✅ If no settings exist, create default settings
    if not settings:
        settings = AdminSettings()
        await settings.insert()

    return settings


@admin_router.put("/settings/")
async def update_admin_settings(
    new_settings: AdminSettings, admin: User = Depends(get_admin_user)
) -> dict[str, str]:
    """Update global admin settings"""

    settings = await AdminSettings.find_one(projection_model=AdminSettings)

    if not settings:
        settings = AdminSettings()

    logger.debug(f"Updating admin settings to new settings: {new_settings}")
    settings.admin_welcome_message = new_settings.admin_welcome_message

    await settings.save()
    logger.debug(f"Admin settings updated: {settings}")

    return {"message": "Admin settings updated successfully"}


@admin_router.get("/users/")
async def get_all_users(
    count: int = Query(10, gt=0, le=100),  # ✅ Limit: max 100 users per request
    cursor: Optional[int] = None,  # ✅ Use created_at as cursor
    admin: User = Depends(get_admin_user),
) -> dict[str, Any]:
    """Retrieve paginated list of all registered users (Admin-only)"""
    query = User.find(projection_model=User)
    query = query.project(UserPublic)  # type: ignore

    # ✅ If cursor is provided, fetch older users
    if cursor:
        query = query.find(User.created_at < cursor, projection_model=User)  # type: ignore

    # ✅ Fetch users sorted by `created_at` (newest first)
    users = await query.sort("-created_at").limit(count).to_list()

    # ✅ Get next cursor (last user's `created_at`)
    next_cursor = users[-1].created_at if users else None

    return {"users": users, "next_cursor": next_cursor}


# @admin_router.get("/users/{user_id}", response_model=UserPublic)
# async def get_user(user_id: str, admin: User = Depends(get_admin_user)) -> UserPublic:
#     user = await User.find_one(User.user_id == user_id, projection_model=User)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user.public_version()


# @admin_router.put("/users/{user_id}", response_model=UserPublic)
# async def update_user(user_id: str, user: User):
#     if user_id not in fake_users_db:
#         raise HTTPException(status_code=404, detail="User not found")
#     fake_users_db[user_id] = user.dict()
#     return fake_users_db[user_id]


# @router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(user_id: str):
#     if user_id not in fake_users_db:
#         raise HTTPException(status_code=404, detail="User not found")
#     del fake_users_db[user_id]
#     return {"message": "User deleted successfully"}


# # 2. Platform Stats (/admin/stats)
# @router.get("/stats", response_model=dict)
# async def get_platform_stats():
#     user_count = len(fake_users_db)
#     return {
#         "user_count": user_count,
#         "active_users": sum(1 for u in fake_users_db.values() if u["active"]),
#     }


# # 3. System-wide Logs (/admin/logs)
# @router.get("/logs", response_model=List[Log])
# async def get_logs() -> list[Log]:
#     return []


# # 4. Role/Permission Management (/admin/roles)
# @router.get("/roles", response_model=List[Role])
# async def get_roles():
#     return fake_roles_db


# @router.post("/roles", response_model=Role)
# async def create_role(role: Role):
#     # Check if the role already exists
#     if any(r["role"] == role.role for r in fake_roles_db):
#         raise HTTPException(status_code=400, detail="Role already exists")
#     fake_roles_db.append(role.dict())
#     return role


# @router.put("/roles/{role_name}", response_model=Role)
# async def update_role(role_name: str, role: Role):
#     for i, r in enumerate(fake_roles_db):
#         if r["role"] == role_name:
#             fake_roles_db[i] = role.dict()
#             return role
#     raise HTTPException(status_code=404, detail="Role not found")


# @router.delete("/roles/{role_name}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_role(role_name: str):
#     role = next((r for r in fake_roles_db if r["role"] == role_name), None)
#     if not role:
#         raise HTTPException(status_code=404, detail="Role not found")
#     fake_roles_db.remove(role)
#     return {"message": f"Role {role_name} deleted successfully"}


# # 5. App-level Configuration (/admin/config)
# @router.get("/config", response_model=Config)
# async def get_config():
#     return fake_config_db


# @router.put("/config", response_model=Config)
# async def update_config(config: Config):
#     fake_config_db.update(config.dict())
#     return fake_config_db
