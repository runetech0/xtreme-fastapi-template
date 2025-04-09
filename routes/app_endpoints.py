from fastapi import APIRouter, HTTPException
from models.app_settings import PublicAppSettings
from app.db.admin_settings import AdminSettings

app_router = APIRouter(prefix="/app", tags=["App Settings"])


@app_router.get("/settings/", response_model=PublicAppSettings)
async def get_app_settings() -> PublicAppSettings:
    """Fetch public app-level settings like subscription price"""
    # raise HTTPException(status_code=500, detail="Admin settings not configured")
    settings = await AdminSettings.find_one(projection_model=AdminSettings)

    if not settings:
        raise HTTPException(status_code=500, detail="Admin settings not configured")

    return PublicAppSettings(
        custom_message="Configure this!",
    )
