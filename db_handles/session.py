import asyncpg  # type: ignore
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.env_reader import EnvReader
from app.logs_config import get_logger

from .base import Base

logger = get_logger()


def get_main_db_url(include_asyncpg: bool = True) -> str:
    url = f"postgresql+asyncpg://{EnvReader.DATABASE_USER}:{EnvReader.DATABASE_PASSWORD}@{EnvReader.DATABASE_HOST}:{EnvReader.DATABASE_PORT}/{EnvReader.DATABASE_NAME}"
    if not include_asyncpg:
        url = url.replace("+asyncpg", "")
    return url


engine = create_async_engine(
    get_main_db_url(),
    echo=False,
)
async_session = async_sessionmaker(engine, expire_on_commit=False, autoflush=True)


def _quote_ident(name: str) -> str:
    # Safe quoting for identifiers like database names
    return '"' + name.replace('"', '""') + '"'


async def ensure_database_exists(
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: int,
    db_name: str,
) -> None:
    maintenance_db = "postgres"

    # 1) connect to the maintenance DB, NOT the target db
    conn = await asyncpg.connect(  # type: ignore
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=maintenance_db,
    )
    try:
        # 2) check if the target DB exists
        exists = await conn.fetchval(  # type: ignore
            "SELECT 1 FROM pg_database WHERE datname = $1",
            db_name,
        )

        # 3) create it if missing
        if not exists:
            # CREATE DATABASE cannot be in a transaction; asyncpg executes single
            # statements in autocommit by default (unless you started a transaction),
            # so this is fine.
            db_ident = _quote_ident(db_name)
            await conn.execute(f"CREATE DATABASE {db_ident}")  # type: ignore
            logger.info(f"Database '{db_name}' created.")

        else:
            logger.info(f"Database '{db_name}' already exists.")

    finally:
        await conn.close()  # type: ignore


async def run_trigger_sql(session: AsyncSession, sql: str) -> None:
    await session.execute(text(sql))
    await session.commit()


async def init_db() -> None:
    logger.info("Initializing the database ...")
    await ensure_database_exists(
        EnvReader.DATABASE_USER,
        EnvReader.DATABASE_PASSWORD,
        EnvReader.DATABASE_HOST,
        EnvReader.DATABASE_PORT,
        EnvReader.DATABASE_NAME,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized!")
