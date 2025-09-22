from typing import Literal, TypedDict


class UserValidationJobCommand(TypedDict):
    job_id: str
    command: Literal["create", "delete"]


class EngagementJobCommand(TypedDict):
    job_id: str
    command: Literal["create", "delete"]
