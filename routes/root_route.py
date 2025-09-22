from fastapi import APIRouter

root_router = APIRouter(tags=["Root"])


@root_router.get("/")
async def root() -> dict[str, str]:
    return {"message": "FastAPI template developed by https://t.me/runetech"}
