from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.data import PROJECTS, SAVES

router = APIRouter(prefix="/projects/{project_id}/saves", tags=["saves"])

ReadHistoryItem = Annotated[str, StringConstraints(pattern=r"^.+#[0-9]+$")]
VariableKey = Annotated[str, StringConstraints(min_length=1)]


class ScenarioRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    revision: str = Field(min_length=1)
    checksum: str = Field(min_length=1)


class Position(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1)
    index: int = Field(ge=0)


class LogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    seq: int = Field(ge=0)
    kind: str = Field(min_length=1)
    payload: dict[str, Any]


class ChoiceResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    at: str = Field(pattern=r"^.+#[0-9]+$")
    choice_id: str = Field(min_length=1)
    selected_index: int = Field(ge=0)


class RngState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    seed: str = Field(min_length=1)
    step: int = Field(ge=0)


class SaveDataV0(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state_version: Literal["0"]
    scenario_ref: ScenarioRef
    position: Position
    variables: dict[VariableKey, str | int | float | bool | None]
    read_history: list[ReadHistoryItem] = Field(default_factory=list)
    log: list[LogEntry] = Field(default_factory=list)
    choice_results: list[ChoiceResult] = Field(default_factory=list)
    rng: RngState

    @field_validator("read_history")
    @classmethod
    def validate_read_history_unique(cls, value: list[ReadHistoryItem]) -> list[ReadHistoryItem]:
        if len(set(value)) != len(value):
            raise ValueError("read_history must not contain duplicates")
        return value


class SaveWriteResponse(BaseModel):
    project_id: str
    slot: str
    saved_at: datetime


class SaveReadResponse(BaseModel):
    project_id: str
    slot: str
    saved_at: datetime
    data: SaveDataV0


@router.put("/{slot}", response_model=SaveWriteResponse)
def put_save(project_id: str, slot: str, payload: SaveDataV0) -> SaveWriteResponse:
    if project_id not in PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    project_saves = SAVES.setdefault(project_id, {})
    saved_at = datetime.now(timezone.utc)
    project_saves[slot] = {"saved_at": saved_at, "data": payload.model_dump()}
    return SaveWriteResponse(project_id=project_id, slot=slot, saved_at=saved_at)


@router.get("/{slot}", response_model=SaveReadResponse)
def get_save(project_id: str, slot: str) -> SaveReadResponse:
    if project_id not in PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    slot_data = SAVES.get(project_id, {}).get(slot)
    if slot_data is None:
        raise HTTPException(status_code=404, detail="Save slot not found")

    return SaveReadResponse(
        project_id=project_id,
        slot=slot,
        saved_at=slot_data["saved_at"],
        data=SaveDataV0(**slot_data["data"]),
    )
