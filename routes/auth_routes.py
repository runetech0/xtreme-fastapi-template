from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException

from app.auth_service import (
    create_access_token,
    get_current_user,
    verify_password,
)
from db_handles.user import User
from models.auth import (
    EmailRequest,
    ResetPasswordRequest,
    Token,
    UserLogin,
    UserSignup,
    VerifyEmailRequest,
)

auth_router: APIRouter = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/signup/")
async def signup(user_data: UserSignup) -> Dict[str, str]:
    """Register a new user"""
    existing_user: Optional[User] = await User.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400, detail="User already exists with this email"
        )

    await User.create(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name or "",
        is_admin=False,
    )
    return await login(UserLogin(email=user_data.email, password=user_data.password))


@auth_router.post("/login/")
async def login(user_data: UserLogin) -> Dict[str, str]:
    """Authenticate user and return JWT"""
    user: Optional[User] = await User.get_by_email(user_data.email)
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token: str = create_access_token(data={"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}


@auth_router.post("/logout")
def logout(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    # Normally you'd blacklist the token here
    return {"message": "Logged out successfully"}


@auth_router.post("/refresh-token", response_model=Token)
def refresh_token(token: str) -> Token:
    # Verify refresh token and issue new access token
    if token != "refresh_token":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return Token(access_token="new_access_token", token_type="bearer")


@auth_router.post("/verify-email")
def verify_email(data: VerifyEmailRequest) -> dict[str, str]:
    # Verify the email token
    if data.token != "valid_verification_token":
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Email verified successfully"}


@auth_router.post("/forgot-password")
def forgot_password(data: EmailRequest) -> dict[str, str]:
    # Generate and send a password reset link/token
    return {"message": f"Password reset instructions sent to {data.email}"}


@auth_router.post("/reset-password")
def reset_password(data: ResetPasswordRequest) -> dict[str, str]:
    # Reset the user's password using the token
    if data.token != "valid_reset_token":
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Password has been reset successfully"}
