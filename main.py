from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.settings import API_DESCRIPTION, API_TITLE, API_VERSION, OPENAPI_VERSION
from app.state import GlobalState
from app.db import init_db  # type: ignore
from typing import AsyncGenerator
from routes.auth_routes import auth_router
from routes.admin_routes import admin_router
from routes.user_routes import user_router
from routes.app_endpoints import app_router
from routes.payment_routes import payments_router
from routes.root_route import root_router
from routes.file_routes import file_router
from app.middlewares.standard_response import (
    StandardResponseMiddleware,
    register_httpexception_handler,
)
from app.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await GlobalState.setup()
    client = await init_db()  # type: ignore[unused-ignore]
    logger.info("Startup complete!")
    yield  # App is running
    logger.info("Running teardown process  ...")
    client.close()  # Cleanup on shutdown
    await GlobalState.teardown()


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
app.include_router(app_router)
app.include_router(payments_router)
app.include_router(file_router)
