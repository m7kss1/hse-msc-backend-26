from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from moderation.domain.models import Listing


class PredictRequest(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "seller_id": 42,
                    "is_verified_seller": False,
                    "item_id": 101,
                    "name": "Велосипед",
                    "description": "Городской велосипед в хорошем состоянии",
                    "category": 3,
                    "images_qty": 0,
                }
            ]
        },
    )

    seller_id: int = Field(gt=0, description="Положительный идентификатор продавца")
    is_verified_seller: bool = Field(description="Подтверждён ли продавец")
    item_id: int = Field(gt=0, description="Положительный идентификатор объявления")
    name: str = Field(min_length=1, description="Непустое название объявления")
    description: str = Field(min_length=1, description="Непустое описание объявления")
    category: int = Field(gt=0, description="Положительный идентификатор категории")
    images_qty: int = Field(ge=0, description="Количество изображений, не меньше нуля")

    def to_domain(self) -> Listing:
        return Listing(
            seller_id=self.seller_id,
            is_verified_seller=self.is_verified_seller,
            item_id=self.item_id,
            name=self.name,
            description=self.description,
            category=self.category,
            images_qty=self.images_qty,
        )


class ValidationIssue(BaseModel):
    loc: list[str | int]
    message: str
    type: str


class ErrorResponse(BaseModel):
    code: Literal["validation_error", "internal_error"]
    message: str
    details: list[ValidationIssue] = Field(default_factory=list)
