from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.env_reader import EnvReader
from app.logger import logger
from app.settings import API_DESCRIPTION, API_TITLE, API_VERSION, OPENAPI_VERSION
from db_handles.session import init_db
from middlewares.standard_response import (
    StandardResponseMiddleware,
    register_httpexception_handler,
)
from routes.admin_routes import admin_router
from routes.auth_routes import auth_router
from routes.file_routes import file_router
from routes.payment_routes import payments_router
from routes.root_route import root_router
from routes.user_routes import user_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    logger.info("Startup complete!")
    yield  # App is running
    logger.info("Running teardown process  ...")


app = FastAPI(
    lifespan=lifespan,
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,  # this is your app version
    openapi_version=OPENAPI_VERSION,  # this is the OpenAPI schema version
)


# Enable CORS Middleware to Handle Preflight (OPTIONS) Requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)
app.add_middleware(StandardResponseMiddleware)
register_httpexception_handler(app)


# Register routes
app.include_router(root_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(payments_router)
app.include_router(file_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host=EnvReader.HOST, port=EnvReader.PORT, reload=EnvReader.VIRCHUAL
    )
