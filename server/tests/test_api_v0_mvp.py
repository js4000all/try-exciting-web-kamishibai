from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def valid_save_payload() -> dict:
    return {
        "state_version": "0",
        "scenario_ref": {
            "name": "main_story",
            "revision": "git:1d73725",
            "checksum": "3e7d6a6b9f9fca145f0f7f8fcbeb2ccac0e8a9df68ad5e8f6f2d7552edce2a00",
        },
        "position": {"label": "intro", "index": 3},
        "variables": {
            "player_name": "Aoi",
            "affinity": 12,
            "met_guide": True,
            "last_seen": None,
        },
        "read_history": ["intro#0", "intro#1", "intro#2"],
        "log": [
            {"seq": 0, "kind": "line", "payload": {"text": "ようこそ"}},
            {"seq": 1, "kind": "choice", "payload": {"id": "c_intro_1"}},
        ],
        "choice_results": [
            {"at": "intro#2", "choice_id": "c_intro_1", "selected_index": 0}
        ],
        "rng": {"seed": "project-1-slot-2-20250101", "step": 14},
    }


def test_get_projects_ok() -> None:
    response = client.get("/api/v0/projects")

    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert body["items"][0]["id"] == "project-1"


def test_get_project_ok() -> None:
    response = client.get("/api/v0/projects/project-1")

    assert response.status_code == 200
    assert response.json()["id"] == "project-1"


def test_get_project_404() -> None:
    response = client.get("/api/v0/projects/project-x")

    assert response.status_code == 404


def test_get_scenario_chapter_ok() -> None:
    response = client.get("/api/v0/projects/project-1/scenario/chapters/prologue")

    assert response.status_code == 200
    assert response.json()["chapter_id"] == "prologue"


def test_get_scenario_chapter_404() -> None:
    response = client.get("/api/v0/projects/project-1/scenario/chapters/not-found")

    assert response.status_code == 404


def test_put_and_get_save_ok() -> None:
    put_response = client.put(
        "/api/v0/projects/project-1/saves/1",
        json=valid_save_payload(),
    )
    assert put_response.status_code == 200

    get_response = client.get("/api/v0/projects/project-1/saves/1")
    assert get_response.status_code == 200
    assert get_response.json()["state_version"] == "0"


def test_get_save_404() -> None:
    response = client.get("/api/v0/projects/project-1/saves/999")

    assert response.status_code == 404


def test_put_save_project_404() -> None:
    response = client.put("/api/v0/projects/project-x/saves/1", json=valid_save_payload())

    assert response.status_code == 404
