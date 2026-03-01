from fastapi.testclient import TestClient

from app.main import app


def test_404_response_uses_error_envelope() -> None:
    client = TestClient(app)

    response = client.get("/api/v0/projects/project-x")

    assert response.status_code == 404
    body = response.json()
    assert set(body.keys()) == {"error"}
    assert body["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert body["error"]["message"] == "Project not found"
    assert body["error"]["detail"] is None
    assert body["error"]["request_id"]
    assert body["error"]["request_id"] == response.headers["X-Request-ID"]


def test_422_response_uses_error_envelope() -> None:
    client = TestClient(app)

    response = client.put("/api/v0/projects/project-1/saves/1", json={"state_version": "0"})

    assert response.status_code == 422
    body = response.json()
    assert set(body.keys()) == {"error"}
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"] == "Request validation failed"
    assert isinstance(body["error"]["detail"], list)
    assert body["error"]["request_id"]
    assert body["error"]["request_id"] == response.headers["X-Request-ID"]
