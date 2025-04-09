from .db.admin_settings import AdminSettings
from .logger import logger


class GlobalState:

    _setup_done: bool = False

    @classmethod
    async def get_admin_settings(cls) -> AdminSettings:
        admin_settings = await AdminSettings.find_one(projection_model=AdminSettings)
        if not admin_settings:
            admin_settings = AdminSettings()
            await admin_settings.save()

        return admin_settings

    @classmethod
    async def setup(cls) -> None:
        logger.info("Running the global state setup ...")
        if not cls._setup_done:
            pass

    @classmethod
    async def teardown(cls) -> None:
        pass
