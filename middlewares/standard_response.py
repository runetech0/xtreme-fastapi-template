import json
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp


class StandardResponseMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            # ✅ Skip middleware for OpenAPI and docs
            if request.url.path in ("/openapi.json", "/docs", "/redoc"):
                return await call_next(request)

            # Get the response
            original_response: Response = await call_next(request)

            # Only wrap JSON responses with 2xx status
            content_type = original_response.headers.get("content-type", "")
            if (
                200 <= original_response.status_code < 300
                and "application/json" in content_type
            ):
                # Manually read the body
                body = b""
                async for chunk in original_response.body_iterator:  # type: ignore
                    body += chunk  # type: ignore

                try:
                    data: Any = json.loads(body)  # type: ignore
                except json.JSONDecodeError:
                    data = body.decode("utf-8")  # type: ignore

                wrapped: Dict[str, Optional[Any]] = {
                    "data": data,
                    "error": None,
                }

                new_body = json.dumps(wrapped).encode("utf-8")

                return StreamingResponse(
                    content=iter([new_body]),
                    status_code=original_response.status_code,
                    headers={
                        k: v
                        for k, v in original_response.headers.items()
                        if k.lower() != "content-length"
                    },
                    media_type="application/json",
                )

            return original_response

        except Exception as e:
            error_body: Dict[str, Optional[Any]] = {
                "data": None,
                "error": {
                    "code": 500,
                    "message": "Internal Server Error",
                    "details": str(e),
                },
            }
            return JSONResponse(status_code=500, content=error_body)


def create_error_response(
    status_code: int, message: str, code: Optional[int] = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "data": None,
            "error": {
                "code": code or status_code,
                "message": message,
            },
        },
    )


def register_httpexception_handler(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(  # pyright: ignore [reportUnusedFunction]
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        return create_error_response(
            status_code=exc.status_code,
            message=exc.detail,
        )
