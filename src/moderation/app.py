from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from moderation.api.errors import internal_error_handler, validation_error_handler
from moderation.api.routes import router


class ModerationApp(FastAPI):
    def openapi(self) -> dict[str, Any]:
        schema = super().openapi()
        # Валидация возвращает 400, поэтому убираем стандартный 422 из схемы
        schema["paths"]["/predict"]["post"]["responses"].pop("422", None)
        return schema


def create_app() -> FastAPI:
    application = ModerationApp(
        title="Модерация объявлений",
        description="POST /predict возвращает true, если объявление содержит нарушения",
        version="0.1.0",
        openapi_tags=[
            {"name": "Moderation", "description": "Модерация объявлений"},
            {"name": "Service", "description": "Доступность сервиса"},
        ],
    )
    application.exception_handler(RequestValidationError)(validation_error_handler)
    application.exception_handler(Exception)(internal_error_handler)
    application.include_router(router)
    return application
