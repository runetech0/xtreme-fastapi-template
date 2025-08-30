from pydantic import BaseModel


class AdminSettingsOutput(BaseModel):
    user_id: int
    app_name: str
    app_version: str
    maintenance_mode: bool
    custom_message: str
    max_users: int
    subscription_price: str
    enable_registration: bool
    enable_file_upload: bool
    admin_email: str
    system_notifications: bool
    debug_mode: bool
    backup_frequency: str


class AdminSettingsUpdate(BaseModel):
    app_name: str | None = None
    app_version: str | None = None
    maintenance_mode: bool | None = None
    custom_message: str | None = None
    max_users: int | None = None
    subscription_price: str | None = None
    enable_registration: bool | None = None
    enable_file_upload: bool | None = None
    admin_email: str | None = None
    system_notifications: bool | None = None
    debug_mode: bool | None = None
    backup_frequency: str | None = None
