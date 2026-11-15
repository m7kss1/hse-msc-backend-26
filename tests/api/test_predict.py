import logging
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from moderation.api.dependencies import get_moderation_service
from moderation.domain.models import Listing
from moderation.repositories.policies import PolicyRepository
from moderation.services.moderation import ModerationService

FIELDS = (
    "seller_id",
    "is_verified_seller",
    "item_id",
    "name",
    "description",
    "category",
    "images_qty",
)


@pytest.mark.parametrize(
    ("verified", "images", "expected"),
    [(True, 0, False), (True, 1, False), (False, 0, True), (False, 1, False), (False, 5, False)],
)
def test_predict_returns_only_json_boolean(
    client: TestClient, payload: dict[str, object], verified: bool, images: int, expected: bool
) -> None:
    payload.update(is_verified_seller=verified, images_qty=images)

    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() is expected
    assert response.text == str(expected).lower()


@pytest.mark.parametrize("field", FIELDS)
def test_every_field_is_required(
    client: TestClient, payload: dict[str, object], field: str
) -> None:
    del payload[field]

    response = client.post("/predict", json=payload)

    assert response.status_code == 400
    assert response.json()["code"] == "validation_error"
    assert response.json()["details"] == [
        {"loc": ["body", field], "message": "Field required", "type": "missing"}
    ]


@pytest.mark.parametrize("field", FIELDS)
def test_null_is_not_accepted(client: TestClient, payload: dict[str, object], field: str) -> None:
    payload[field] = None

    response = client.post("/predict", json=payload)

    assert response.status_code == 400
    assert response.json()["details"][0]["loc"] == ["body", field]


@pytest.mark.parametrize("field", ["seller_id", "item_id", "category", "images_qty"])
@pytest.mark.parametrize("value", ["1", 1.0, True, [], {}])
def test_integer_fields_reject_other_types(
    client: TestClient, payload: dict[str, object], field: str, value: object
) -> None:
    payload[field] = value

    response = client.post("/predict", json=payload)

    assert response.status_code == 400
    assert response.json()["details"][0]["type"] == "int_type"


@pytest.mark.parametrize("value", ["true", "false", "yes", 0, 1, [], {}])
def test_verified_flag_requires_a_real_boolean(
    client: TestClient, payload: dict[str, object], value: object
) -> None:
    payload["is_verified_seller"] = value

    response = client.post("/predict", json=payload)

    assert response.status_code == 400
    assert response.json()["details"][0]["type"] == "bool_type"


@pytest.mark.parametrize("field", ["name", "description"])
@pytest.mark.parametrize("value", [1, True, [], {}])
def test_text_fields_require_strings(
    client: TestClient, payload: dict[str, object], field: str, value: object
) -> None:
    payload[field] = value

    response = client.post("/predict", json=payload)

    assert response.status_code == 400
    assert response.json()["details"][0]["type"] == "string_type"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("seller_id", 0),
        ("seller_id", -1),
        ("item_id", 0),
        ("item_id", -1),
        ("category", 0),
        ("category", -1),
        ("images_qty", -1),
        ("name", ""),
        ("name", " \t\n "),
        ("description", ""),
        ("description", " \t\n "),
    ],
)
def test_invalid_values(
    client: TestClient, payload: dict[str, object], field: str, value: object
) -> None:
    payload[field] = value

    response = client.post("/predict", json=payload)

    assert response.status_code == 400
    assert response.json()["code"] == "validation_error"
    assert response.json()["details"][0]["loc"] == ["body", field]


def test_extra_fields_are_rejected(client: TestClient, payload: dict[str, object]) -> None:
    payload["unexpected"] = "value"

    response = client.post("/predict", json=payload)

    assert response.status_code == 400
    assert response.json()["details"][0]["type"] == "extra_forbidden"


@pytest.mark.parametrize("body", ["", "{broken json", "[]", '"text"', "null", "42"])
def test_invalid_body(client: TestClient, body: str) -> None:
    response = client.post("/predict", content=body, headers={"Content-Type": "application/json"})

    assert response.status_code == 400
    assert response.json()["code"] == "validation_error"
    assert response.json()["details"]


def test_validation_errors_do_not_echo_user_data(
    client: TestClient, payload: dict[str, object]
) -> None:
    payload["seller_id"] = "sensitive-invalid-input"

    response = client.post("/predict", json=payload)

    assert response.status_code == 400
    assert "sensitive-invalid-input" not in response.text


def test_handler_passes_normalized_listing_to_service(
    app: FastAPI, client: TestClient, payload: dict[str, object], listing: Listing
) -> None:
    service = Mock(spec=ModerationService)
    service.predict.return_value = True
    app.dependency_overrides[get_moderation_service] = lambda: service
    payload.update(name="  Велосипед  ", description="  Городской велосипед в хорошем состоянии.  ")

    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert response.json() is True
    service.predict.assert_called_once_with(listing)


@pytest.mark.parametrize("failure_layer", ["service", "repository", "dependency"])
def test_internal_failure_returns_safe_500(
    app: FastAPI,
    client: TestClient,
    payload: dict[str, object],
    caplog: pytest.LogCaptureFixture,
    failure_layer: str,
) -> None:
    error = RuntimeError("private connection details")
    if failure_layer == "service":
        service = Mock(spec=ModerationService)
        service.predict.side_effect = error
        app.dependency_overrides[get_moderation_service] = lambda: service
    elif failure_layer == "repository":
        repository = Mock(spec=PolicyRepository)
        repository.get_policy.side_effect = error
        app.dependency_overrides[get_moderation_service] = lambda: ModerationService(repository)
    else:

        def broken_dependency() -> ModerationService:
            raise error

        app.dependency_overrides[get_moderation_service] = broken_dependency

    with caplog.at_level(logging.ERROR, logger="moderation.api.errors"):
        response = client.post("/predict", json=payload)

    assert response.status_code == 500
    assert response.json() == {
        "code": "internal_error",
        "message": "Внутренняя ошибка сервиса.",
        "details": [],
    }
    assert "private connection details" not in response.text
    assert "Unhandled error during POST /predict" in caplog.text
    assert "private connection details" in caplog.text


def test_invalid_request_never_reaches_business_logic(
    app: FastAPI, client: TestClient, payload: dict[str, object]
) -> None:
    service = Mock(spec=ModerationService)
    app.dependency_overrides[get_moderation_service] = lambda: service
    payload["images_qty"] = -1

    assert client.post("/predict", json=payload).status_code == 400
    service.predict.assert_not_called()
