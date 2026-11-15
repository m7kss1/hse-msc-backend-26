from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Listing:
    seller_id: int
    is_verified_seller: bool
    item_id: int
    name: str
    description: str
    category: int
    images_qty: int


@dataclass(frozen=True, slots=True)
class ModerationPolicy:
    minimum_images: int = 1
