from fastapi.testclient import TestClient

from app.main import app


def make_save_payload() -> dict:
    return {
        "state_version": "0",
        "scenario_ref": {
            "name": "project-1",
            "revision": "2026.02.01",
            "checksum": "abc123",
        },
        "position": {"label": "start", "index": 0},
        "variables": {"flag": True, "score": 10, "name": "hero", "unused": None},
        "read_history": ["prologue#0"],
        "log": [{"seq": 0, "kind": "say", "payload": {"text": "hello"}}],
        "choice_results": [
            {"at": "prologue#1", "choice_id": "choice-1", "selected_index": 0}
        ],
        "rng": {"seed": "seed-1", "step": 3},
    }


def test_get_projects_success() -> None:
    client = TestClient(app)

    response = client.get("/api/v0/projects")

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == "project-1"


def test_get_project_success() -> None:
    client = TestClient(app)

    response = client.get("/api/v0/projects/project-1")

    assert response.status_code == 200
    assert response.json()["assets_base_url"] == "/api/v0/assets/project-1/"


def test_get_project_not_found() -> None:
    client = TestClient(app)

    response = client.get("/api/v0/projects/project-x")

    assert response.status_code == 404


def test_get_chapter_scenario_success() -> None:
    client = TestClient(app)

    response = client.get("/api/v0/projects/project-1/scenario/chapters/prologue")

    assert response.status_code == 200
    body = response.json()
    assert body["scenario"]["id"] == "prologue"
    assert body["warnings"] == []


def test_get_chapter_scenario_not_found_chapter() -> None:
    client = TestClient(app)

    response = client.get("/api/v0/projects/project-1/scenario/chapters/missing")

    assert response.status_code == 404


def test_get_chapter_scenario_not_found_project() -> None:
    client = TestClient(app)

    response = client.get("/api/v0/projects/project-x/scenario/chapters/prologue")

    assert response.status_code == 404


def test_put_and_get_save_success() -> None:
    client = TestClient(app)
    payload = make_save_payload()

    put_response = client.put("/api/v0/projects/project-1/saves/1", json=payload)

    assert put_response.status_code == 200
    put_body = put_response.json()
    assert put_body["project_id"] == "project-1"
    assert put_body["slot"] == "1"

    get_response = client.get("/api/v0/projects/project-1/saves/1")

    assert get_response.status_code == 200
    get_body = get_response.json()
    assert get_body["project_id"] == "project-1"
    assert get_body["slot"] == "1"
    assert get_body["data"]["state_version"] == "0"


def test_put_save_project_not_found() -> None:
    client = TestClient(app)

    response = client.put("/api/v0/projects/project-x/saves/1", json=make_save_payload())

    assert response.status_code == 404


def test_get_save_not_found_slot() -> None:
    client = TestClient(app)

    response = client.get("/api/v0/projects/project-1/saves/missing")

    assert response.status_code == 404


def test_get_save_not_found_project() -> None:
    client = TestClient(app)

    response = client.get("/api/v0/projects/project-x/saves/1")

    assert response.status_code == 404
