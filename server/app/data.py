from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

PROJECTS: dict[str, dict[str, Any]] = {
    "project-1": {
        "id": "project-1",
        "title": "Sample Project",
        "summary": "v0 sample",
        "entry_chapter": "prologue",
        "updated_at": datetime(2026, 2, 1, 9, 30, tzinfo=timezone.utc),
        "chapters": ["prologue", "chapter-1"],
        "scenario_revision": "2026.02.01",
    }
}

SCENARIOS: dict[str, dict[str, dict[str, Any]]] = {
    "project-1": {
        "prologue": {
            "id": "prologue",
            "nodes": [
                {"type": "label", "name": "start"},
                {"type": "say", "speaker": "Narrator", "text": "Welcome to Kamishibai."},
            ],
        }
    }
}

SAVES: dict[str, dict[str, dict[str, Any]]] = {}
