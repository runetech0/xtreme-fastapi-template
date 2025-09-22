from redis.asyncio import Redis

from app.env_reader import EnvReader
from app.logs_config import get_logger

logger = get_logger()


async def get_new_redis_client() -> Redis:
    logger.info("Getting a new redis client ...")
    return Redis(
        host=EnvReader.REDIS_HOST, port=EnvReader.REDIS_PORT, db=EnvReader.REDIS_DB
    )
