from typing import Annotated

from fastapi import APIRouter, Depends, status

from moderation.api.dependencies import get_moderation_service
from moderation.api.schemas import ErrorResponse, PredictRequest
from moderation.services.moderation import ModerationService

router = APIRouter()


@router.get("/", tags=["Service"], summary="Проверить доступность сервиса")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@router.post(
    "/predict",
    tags=["Moderation"],
    summary="Проверить объявление на нарушения",
    description=(
        "Возвращает JSON boolean: true при наличии нарушений, false при их отсутствии. "
        "Подтверждённый продавец всегда проходит проверку, неподтверждённому "
        "нужно хотя бы одно изображение"
    ),
    response_model=bool,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Результат модерации: true при наличии нарушений"},
        400: {"model": ErrorResponse, "description": "Невалидный запрос"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервиса"},
    },
)
def predict(
    payload: PredictRequest,
    service: Annotated[ModerationService, Depends(get_moderation_service)],
) -> bool:
    return service.predict(payload.to_domain())
