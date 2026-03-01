from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.data import PROJECTS, SCENARIOS

router = APIRouter(prefix="/projects/{project_id}/scenario", tags=["scenario"])


class ScenarioV0(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    nodes: list[dict[str, Any]] = Field(min_length=1)


class ChapterScenarioResponse(BaseModel):
    project_id: str
    chapter_id: str
    scenario: ScenarioV0
    warnings: list[str]


@router.get("/chapters/{chapter_id}", response_model=ChapterScenarioResponse)
def get_chapter_scenario(project_id: str, chapter_id: str) -> ChapterScenarioResponse:
    if project_id not in PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    chapter_scenario = SCENARIOS.get(project_id, {}).get(chapter_id)
    if chapter_scenario is None:
        raise HTTPException(status_code=404, detail="Chapter not found")

    return ChapterScenarioResponse(
        project_id=project_id,
        chapter_id=chapter_id,
        scenario=ScenarioV0(**chapter_scenario),
        warnings=[],
    )
