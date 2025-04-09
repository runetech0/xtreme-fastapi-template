from beanie import Document


class AdminSettings(Document):
    """Model for storing admin-configurable settings"""

    admin_welcome_message: str = "Hey Admin, welcome!"

    class Settings:
        collection = "admin_settings"

    async def fetch_fresh(self) -> "AdminSettings":
        update = await AdminSettings.find_one(projection_model=AdminSettings)
        if not update:
            raise ValueError("Update not found")
        return update
