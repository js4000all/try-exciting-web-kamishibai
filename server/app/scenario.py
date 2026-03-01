from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .models import ScenarioChapterResponse, ScenarioV0
from .projects import PROJECTS

router = APIRouter(prefix="/api/v0/projects/{project_id}/scenario", tags=["scenario"])

SCENARIOS: dict[tuple[str, str], ScenarioV0] = {
    (
        "project-1",
        "prologue",
    ): ScenarioV0(
        id="main_story",
        nodes=[
            {"type": "label", "name": "start"},
            {"type": "say", "speaker": "Narrator", "text": "ようこそ"},
            {
                "type": "choice",
                "prompt": "進みますか？",
                "options": [
                    {"text": "はい", "jump": "chapter_1"},
                    {"text": "いいえ", "jump": "end"},
                ],
            },
        ],
    )
}


@router.get("/chapters/{chapter_id}", response_model=ScenarioChapterResponse)
def get_chapter(project_id: str, chapter_id: str) -> ScenarioChapterResponse:
    if project_id not in PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    scenario = SCENARIOS.get((project_id, chapter_id))
    if scenario is None:
        raise HTTPException(status_code=404, detail="Chapter not found")

    return ScenarioChapterResponse(
        project_id=project_id,
        chapter_id=chapter_id,
        scenario=scenario,
        warnings=[],
    )
