from pydantic import BaseModel
from datetime import datetime


class Role(BaseModel):
    role: str
    permissions: list[str]


class Config(BaseModel):
    app_name: str
    version: str


class Log(BaseModel):
    timestamp: datetime
    action: str
    user_id: str
