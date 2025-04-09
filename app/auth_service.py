from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
from passlib.context import CryptContext
import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from .env_reader import EnvReader
from .db.user import User
from app.settings import JWT_PROCESSING_ALGORITHM


# Password hashing
pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="auth/login")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return str(pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password"""
    return bool(pwd_context.verify(plain_password, hashed_password))


def create_access_token(
    data: Dict[str, str | int], expires_delta_days: Optional[timedelta] = None
) -> str:
    """Generate a JWT token"""
    to_encode: Dict[str, str | int] = data.copy()
    expire: datetime = datetime.now(timezone.utc) + (
        expires_delta_days or timedelta(days=EnvReader.ACCESS_TOKEN_EXPIRES_DAYS)
    )
    to_encode.update({"exp": int(expire.timestamp())})

    return str(
        jwt.encode(
            to_encode, EnvReader.JWT_SECRET_KEY, algorithm=JWT_PROCESSING_ALGORITHM
        )
    )


async def get_current_user(token: str = Security(oauth2_scheme)) -> User:
    """Decode JWT and return authenticated user"""
    try:
        payload: Dict[str, str] = jwt.decode(
            token, EnvReader.JWT_SECRET_KEY, algorithms=[JWT_PROCESSING_ALGORITHM]
        )
        user_id: Optional[str] = payload.get("user_id")  # Extract `user_id`
        if user_id is None:
            raise HTTPException(status_code=401, detail="Not Logged-in")
        user: Optional[User] = await User.find_one(
            User.user_id == user_id, projection_model=User
        )  # Query by `user_id`
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:

        raise HTTPException(status_code=401, detail="Invalid Login Token")


async def get_admin_user(user: User = Depends(get_current_user)) -> User:
    """Ensure the authenticated user is an admin"""
    if not user.is_admin:
        raise HTTPException(
            status_code=403, detail="Admin access required to perform this operation"
        )
    return user
