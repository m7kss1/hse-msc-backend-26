import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from moderation.api.schemas import ErrorResponse, ValidationIssue

logger = logging.getLogger(__name__)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    error = ErrorResponse(
        code="validation_error",
        message="Некорректный запрос.",
        details=[
            ValidationIssue(loc=list(issue["loc"]), message=issue["msg"], type=issue["type"])
            for issue in exc.errors()
        ],
    )
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error.model_dump())


async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled error during %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    error = ErrorResponse(code="internal_error", message="Внутренняя ошибка сервиса.")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error.model_dump()
    )
