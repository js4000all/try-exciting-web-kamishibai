from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from .models import ProjectDetailResponse, ProjectListResponse, ProjectSummary

router = APIRouter(prefix="/api/v0/projects", tags=["projects"])

PROJECTS: dict[str, ProjectDetailResponse] = {
    "project-1": ProjectDetailResponse(
        id="project-1",
        title="Sample Project",
        summary="v0 sample",
        entry_chapter="prologue",
        chapters=["prologue", "chapter-1"],
        scenario_revision="2026.02.01",
        assets_base_url="/api/v0/assets/project-1/",
    )
}

UPDATED_AT: dict[str, datetime] = {
    "project-1": datetime(2026, 2, 1, 9, 30, tzinfo=UTC),
}


@router.get("", response_model=ProjectListResponse)
def list_projects() -> ProjectListResponse:
    items = [
        ProjectSummary(
            id=project.id,
            title=project.title,
            summary=project.summary,
            entry_chapter=project.entry_chapter,
            updated_at=UPDATED_AT[project.id],
        )
        for project in PROJECTS.values()
    ]
    return ProjectListResponse(items=items)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(project_id: str) -> ProjectDetailResponse:
    project = PROJECTS.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
