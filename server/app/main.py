import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
import uvicorn

from app.api_v0 import router as api_v0_router
from app.errors import (
    AppError,
    app_error_response,
    http_error_response,
    internal_error_response,
    validation_error_response,
)
from app.request_context import request_id_middleware

logger = logging.getLogger(__name__)

app = FastAPI(title="kamishibai-server", version="0.1.0")
app.middleware("http")(request_id_middleware)
app.include_router(api_v0_router)


@app.exception_handler(AppError)
def handle_app_error(request: Request, exc: AppError):
    logger.warning(
        "app_error code=%s request_id=%s message=%s",
        exc.code,
        getattr(request.state, "request_id", ""),
        exc.message,
    )
    return app_error_response(request, exc)


@app.exception_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError):
    logger.warning(
        "validation_error request_id=%s",
        getattr(request.state, "request_id", ""),
    )
    return validation_error_response(request, exc)


@app.exception_handler(HTTPException)
def handle_http_error(request: Request, exc: HTTPException):
    logger.warning(
        "http_error status=%s request_id=%s",
        exc.status_code,
        getattr(request.state, "request_id", ""),
    )
    return http_error_response(request, exc)


@app.exception_handler(Exception)
def handle_internal_error(request: Request, exc: Exception):
    logger.exception(
        "internal_error request_id=%s",
        getattr(request.state, "request_id", ""),
        exc_info=exc,
    )
    return internal_error_response(request, exc)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "api": "v0"}


def run() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
