from typing import Optional
from pydantic import BaseModel


class PublicAppSettings(BaseModel):
    custom_message: Optional[str]
