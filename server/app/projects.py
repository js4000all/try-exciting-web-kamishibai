from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.data import PROJECTS
from app.errors import ResourceNotFoundError

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectSummary(BaseModel):
    id: str
    title: str
    summary: str
    entry_chapter: str
    updated_at: datetime


class ProjectListResponse(BaseModel):
    items: list[ProjectSummary]


class ProjectDetailResponse(BaseModel):
    id: str
    title: str
    summary: str
    entry_chapter: str
    chapters: list[str]
    scenario_revision: str
    assets_base_url: str


@router.get("", response_model=ProjectListResponse)
def get_projects() -> ProjectListResponse:
    items = [ProjectSummary(**project) for project in PROJECTS.values()]
    return ProjectListResponse(items=items)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(project_id: str) -> ProjectDetailResponse:
    project = PROJECTS.get(project_id)
    if project is None:
        raise ResourceNotFoundError("Project not found")

    return ProjectDetailResponse(
        **project,
        assets_base_url=f"/api/v0/assets/{project_id}/",
    )
