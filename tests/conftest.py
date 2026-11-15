from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from moderation.app import create_app
from moderation.domain.models import Listing


@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    # Иначе TestClient пробрасывает исключение вместо ответа 500
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def payload() -> dict[str, object]:
    return {
        "seller_id": 42,
        "is_verified_seller": False,
        "item_id": 101,
        "name": "Велосипед",
        "description": "Городской велосипед в хорошем состоянии.",
        "category": 3,
        "images_qty": 0,
    }


@pytest.fixture
def listing() -> Listing:
    return Listing(
        seller_id=42,
        is_verified_seller=False,
        item_id=101,
        name="Велосипед",
        description="Городской велосипед в хорошем состоянии.",
        category=3,
        images_qty=0,
    )
