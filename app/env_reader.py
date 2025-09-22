import os

from dotenv import load_dotenv

load_dotenv()


class EnvReader:
    FRONTEND_HOST: str = os.getenv("FRONTEND_HOST", "localhost:3000")
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "localhost:8000")
    # JWT Variables
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "superrrrrrrrrrrlongggggggnonnnnnnexistinggggsecretttttt"
    )
    ACCESS_TOKEN_EXPIRES_DAYS: int = int(os.getenv("ACCESS_TOKEN_EXPIRES_DAYS", 30))

    # Postgres Variables
    DATABASE_USER: str = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "postgres")
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", 5432))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "postgres")

    # NowPayments Variables
    NOWPAYMENTS_IPN_KEY: str = os.getenv("NOWPAYMENTS_IPN_KEY", "")
    NOWPAYMENTS_API_KEY: str = os.getenv("NOWPAYMENTS_API_KEY", "")

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

    VIRCHUAL = bool(os.getenv("VIRCHUAL", "false"))

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
