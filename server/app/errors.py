from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ErrorCode(StrEnum):
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    HTTP_ERROR = "HTTP_ERROR"


@dataclass(slots=True)
class AppError(Exception):
    code: ErrorCode
    message: str
    detail: Any
    status_code: int


class ResourceNotFoundError(AppError):
    def __init__(self, message: str, detail: Any = None) -> None:
        super().__init__(
            code=ErrorCode.RESOURCE_NOT_FOUND,
            message=message,
            detail=detail,
            status_code=404,
        )


class ValidationError(AppError):
    def __init__(self, message: str, detail: Any = None) -> None:
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            detail=detail,
            status_code=422,
        )


def error_envelope(*, code: str, message: str, detail: Any, request_id: str) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "detail": detail,
            "request_id": request_id,
        }
    }


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "")


def app_error_response(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_envelope(
            code=exc.code,
            message=exc.message,
            detail=exc.detail,
            request_id=_request_id(request),
        ),
    )


def validation_error_response(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=error_envelope(
            code=ErrorCode.VALIDATION_ERROR,
            message="Request validation failed",
            detail=exc.errors(),
            request_id=_request_id(request),
        ),
    )


def http_error_response(request: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    return JSONResponse(
        status_code=exc.status_code,
        content=error_envelope(
            code=ErrorCode.HTTP_ERROR,
            message=message,
            detail=exc.detail,
            request_id=_request_id(request),
        ),
    )


def internal_error_response(request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=error_envelope(
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            message="Internal server error",
            detail=None,
            request_id=_request_id(request),
        ),
    )
