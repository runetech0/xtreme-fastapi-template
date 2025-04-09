# type: ignore
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from .user import User
from .admin_settings import AdminSettings
from app.env_reader import EnvReader
from app.logger import logger


async def init_db() -> AsyncIOMotorClient:
    """Initialize MongoDB connection and return client."""
    client: AsyncIOMotorClient = AsyncIOMotorClient(EnvReader.MONGO_URI)
    database: AsyncIOMotorDatabase = client[EnvReader.MONGODB_DB_NAME]

    # Initialize Beanie ODM
    await init_beanie(database, document_models=[User, AdminSettings])
    logger.debug(
        f"Connected to db on {EnvReader.MONGO_URI}@{EnvReader.MONGODB_DB_NAME}"
    )
    return client
