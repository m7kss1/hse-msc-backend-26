from fastapi.testclient import TestClient


def test_root(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_openapi_matches_actual_contract(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    operation = schema["paths"]["/predict"]["post"]
    assert set(operation["responses"]) == {"200", "400", "500"}
    assert (
        operation["responses"]["200"]["content"]["application/json"]["schema"]["type"] == "boolean"
    )
    request = schema["components"]["schemas"]["PredictRequest"]
    assert set(request["required"]) == {
        "seller_id",
        "is_verified_seller",
        "item_id",
        "name",
        "description",
        "category",
        "images_qty",
    }
    assert request["additionalProperties"] is False
    assert client.get("/openapi.json").json() == schema


def test_main_exports_application() -> None:
    from main import app

    with TestClient(app) as client:
        assert client.get("/").json() == {"message": "Hello World"}
