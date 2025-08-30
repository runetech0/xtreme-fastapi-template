from typing import Any

from sqlalchemy import Boolean, Integer, String, Text, select
from sqlalchemy.orm import Mapped, mapped_column

from models.admin_settings import AdminSettingsOutput

from .base import Base
from .session import async_session


class AdminSettings(Base):
    __tablename__ = "admin_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # App settings
    app_name: Mapped[str] = mapped_column(
        String(100), default="Xtreme FastAPI Template"
    )
    app_version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    maintenance_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    custom_message: Mapped[str] = mapped_column(
        Text, default="Welcome to our application!"
    )
    max_users: Mapped[int] = mapped_column(Integer, default=1000)
    subscription_price: Mapped[str] = mapped_column(String(20), default="9.99")
    enable_registration: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_file_upload: Mapped[bool] = mapped_column(Boolean, default=True)

    # Admin settings
    admin_email: Mapped[str] = mapped_column(String(100), default="admin@example.com")
    system_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    debug_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    backup_frequency: Mapped[str] = mapped_column(String(20), default="daily")

    @classmethod
    async def get_settings(cls) -> "AdminSettings":
        """
        Get the admin settings from database. Creates default settings if none exist.
        There will only be one row in the admin_settings table.
        """
        async with async_session() as session:
            # Try to get existing settings
            result = await session.execute(select(cls).limit(1))
            settings = result.scalar_one_or_none()

            if settings is None:
                # Create default settings if none exist
                settings = cls()
                session.add(settings)
                await session.commit()
                await session.refresh(settings)

            return settings

    @classmethod
    async def update_settings(cls, **kwargs: Any) -> "AdminSettings":
        """
        Update admin settings with provided values.

        Args:
            **kwargs: Settings attributes to update

        Returns:
            AdminSettings: The updated settings object
        """
        settings = await cls.get_settings()

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

    # Individual update methods for app settings
    @classmethod
    async def update_app_name(cls, app_name: str) -> "AdminSettings":
        """Update app name"""
        return await cls.update_settings(app_name=app_name)

    @classmethod
    async def update_app_version(cls, app_version: str) -> "AdminSettings":
        """Update app version"""
        return await cls.update_settings(app_version=app_version)

    @classmethod
    async def update_maintenance_mode(cls, maintenance_mode: bool) -> "AdminSettings":
        """Update maintenance mode"""
        return await cls.update_settings(maintenance_mode=maintenance_mode)

    @classmethod
    async def update_custom_message(cls, custom_message: str) -> "AdminSettings":
        """Update custom message"""
        return await cls.update_settings(custom_message=custom_message)

    @classmethod
    async def update_max_users(cls, max_users: int) -> "AdminSettings":
        """Update max users"""
        return await cls.update_settings(max_users=max_users)

    @classmethod
    async def update_subscription_price(
        cls, subscription_price: str
    ) -> "AdminSettings":
        """Update subscription price"""
        return await cls.update_settings(subscription_price=subscription_price)

    @classmethod
    async def update_enable_registration(
        cls, enable_registration: bool
    ) -> "AdminSettings":
        """Update enable registration"""
        return await cls.update_settings(enable_registration=enable_registration)

    @classmethod
    async def update_enable_file_upload(
        cls, enable_file_upload: bool
    ) -> "AdminSettings":
        """Update enable file upload"""
        return await cls.update_settings(enable_file_upload=enable_file_upload)

    # Individual update methods for admin settings
    @classmethod
    async def update_admin_email(cls, admin_email: str) -> "AdminSettings":
        """Update admin email"""
        return await cls.update_settings(admin_email=admin_email)

    @classmethod
    async def update_system_notifications(
        cls, system_notifications: bool
    ) -> "AdminSettings":
        """Update system notifications"""
        return await cls.update_settings(system_notifications=system_notifications)

    @classmethod
    async def update_debug_mode(cls, debug_mode: bool) -> "AdminSettings":
        """Update debug mode"""
        return await cls.update_settings(debug_mode=debug_mode)

    @classmethod
    async def update_backup_frequency(cls, backup_frequency: str) -> "AdminSettings":
        """Update backup frequency"""
        return await cls.update_settings(backup_frequency=backup_frequency)

    def output_version(self) -> AdminSettingsOutput:
        return AdminSettingsOutput(
            user_id=self.id,
            app_name=self.app_name,
            app_version=self.app_version,
            maintenance_mode=self.maintenance_mode,
            custom_message=self.custom_message,
            max_users=self.max_users,
            subscription_price=self.subscription_price,
            enable_registration=self.enable_registration,
            enable_file_upload=self.enable_file_upload,
            admin_email=self.admin_email,
            system_notifications=self.system_notifications,
            debug_mode=self.debug_mode,
            backup_frequency=self.backup_frequency,
        )
