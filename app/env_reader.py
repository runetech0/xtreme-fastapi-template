from dotenv import load_dotenv
import os

load_dotenv()


class EnvReader:

    MONGO_URI: str = os.getenv(
        "MONGO_DB_URL",
        "mongodb://localhost:27017",
    )
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "x-db-non-production")
    FRONTEND_DOMAIN: str = os.getenv("FRONTEND_DOMAIN", "localhost:3000")
    API_DOMAIN: str = os.getenv("API_DOMAIN", "localhost:8000")
    NOWPAYMENTS_IPN_KEY = os.getenv("NOWPAYMENTS_IPN_KEY", "")
    NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY", "")

    # JWT Variables
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "superrrrrrrrrrrlongggggggnonnnnnnexistinggggsecretttttt"
    )
    ACCESS_TOKEN_EXPIRES_DAYS: int = int(os.getenv("ACCESS_TOKEN_EXPIRES_DAYS", 30))
    DISABLE_PAID_SUBSCRIPTION: bool = bool(
        os.getenv("DISABLE_PAID_SUBSCRIPTION", False)
    )
