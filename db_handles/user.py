from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils import hash_password
from models.user import UserPublic

from .base import Base
from .session import async_session
from .settings import UserSettings


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Relationship to UserSettings
    settings: Mapped["UserSettings | None"] = relationship(
        "UserSettings",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @classmethod
    async def create(
        cls,
        email: str,
        password: str,
        full_name: str,
        is_admin: bool = False,
        is_blocked: bool = False,
    ) -> "User":
        user = cls(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            is_admin=is_admin,
            is_blocked=is_blocked,
        )
        async with async_session() as session:
            async with session.begin():
                session.add(user)
                await session.flush()  # Get the user ID

                # Create default settings for the user
                user_settings = UserSettings()
                user.settings = user_settings
                session.add(user_settings)

            await session.commit()
        return user

    @classmethod
    async def get_by_id(cls, id: int) -> "User | None":
        async with async_session() as session:
            result = await session.execute(select(cls).where(cls.id == id))
            return result.scalar_one_or_none()

    @classmethod
    async def get_by_email(cls, email: str) -> "User | None":
        """
        Find a user by their email.

        Args:
            email (str): The email to search for

        Returns:
            User | None: The user if found, None otherwise
        """
        async with async_session() as session:
            result = await session.execute(select(cls).where(cls.email == email))
            return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls) -> list["User"]:
        async with async_session() as session:
            result = await session.execute(select(cls))
            return list(result.scalars().all())

    @classmethod
    async def get_count(cls) -> int:
        """
        Get the total count of users in the database.

        Returns:
            int: The total number of users
        """
        async with async_session() as session:
            result = await session.execute(select(cls))
            return len(result.scalars().all())

    @classmethod
    async def get_admin_users(cls) -> list["User"]:
        """
        Get all admin users from the database.

        Returns:
            list[User]: List of users where is_admin is True
        """
        async with async_session() as session:
            result = await session.execute(select(cls).where(cls.is_admin == True))  # noqa: E712
            return list(result.scalars().all())

    @classmethod
    async def get_unblocked_users(cls) -> list["User"]:
        """
        Get all unblocked users from the database.

        Returns:
            list[User]: List of users where is_blocked is False
        """
        async with async_session() as session:
            result = await session.execute(select(cls).where(cls.is_blocked == False))  # noqa: E712
            return list(result.scalars().all())

    async def make_admin(self) -> bool:
        """
        Make the user an admin.

        Returns:
            bool: True if the user was successfully made admin, False if user not found
        """
        async with async_session() as session:
            async with session.begin():
                stmt = select(User).where(User.id == self.id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    return False  # User not found

                user.is_admin = True
                session.add(user)
                await session.commit()
                return True

    async def remove_admin(self) -> bool:
        """
        Remove admin permissions from the user.

        Returns:
            bool: True if admin permissions were successfully removed, False if user not found
        """
        async with async_session() as session:
            async with session.begin():
                stmt = select(User).where(User.id == self.id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    return False  # User not found

                user.is_admin = False
                session.add(user)
                await session.commit()
                return True

    async def block_user(self) -> bool:
        """
        Block the user.

        Returns:
            bool: True if the user was successfully blocked, False if user not found
        """
        async with async_session() as session:
            async with session.begin():
                stmt = select(User).where(User.id == self.id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    return False  # User not found

                user.is_blocked = True
                session.add(user)
                await session.commit()
                return True

    async def unblock_user(self) -> bool:
        """
        Unblock the user.

        Returns:
            bool: True if the user was successfully unblocked, False if user not found
        """
        async with async_session() as session:
            async with session.begin():
                stmt = select(User).where(User.id == self.id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    return False  # User not found

                user.is_blocked = False
                session.add(user)
                await session.commit()
                return True

    async def delete(self) -> None:
        """
        Delete the user from the database.
        """
        async with async_session() as session:
            async with session.begin():
                await session.delete(self)
                await session.commit()

    async def get_settings(self) -> "UserSettings":
        """
        Get or create user settings for this user.

        Returns:
            UserSettings: The user's settings object
        """
        if self.settings is None:
            # Create new settings if none exist
            self.settings = UserSettings()
            async with async_session() as session:
                async with session.begin():
                    session.add(self.settings)
                    await session.commit()
                    await session.refresh(self.settings)

        return self.settings

    async def update_settings(self, **kwargs: Any) -> "UserSettings":
        """
        Update user settings with provided values.

        Args:
            **kwargs: Settings attributes to update

        Returns:
            UserSettings: The updated settings object
        """
        settings = await self.get_settings()

        # Update settings attributes
        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        # Save changes to database
        async with async_session() as session:
            async with session.begin():
                session.add(settings)
                await session.commit()
                await session.refresh(settings)

        return settings

    async def update_password(self, new_password: str) -> bool:
        """
        Update the user's password.

        Args:
            new_password (str): The new password to hash and store

        Returns:
            bool: True if password was successfully updated, False if user not found
        """
        async with async_session() as session:
            async with session.begin():
                stmt = select(User).where(User.id == self.id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    return False  # User not found

                user.hashed_password = hash_password(new_password)
                session.add(user)
                await session.commit()
                return True

    def public_version(self) -> "UserPublic":
        return UserPublic(
            user_id=str(self.id),
            email=self.email,
            full_name=self.full_name,
            is_admin=self.is_admin,
            created_at=int(self.created_at.timestamp()),
        )
