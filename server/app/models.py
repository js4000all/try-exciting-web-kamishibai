from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


NonEmptyStr = Annotated[str, StringConstraints(min_length=1)]
LabelPatternStr = Annotated[str, StringConstraints(pattern=r"^[A-Za-z_][A-Za-z0-9_-]*$")]
VariablePathStr = Annotated[str, StringConstraints(pattern=r"^[A-Za-z_][A-Za-z0-9_.-]*$")]
HistoryEntryStr = Annotated[str, StringConstraints(pattern=r"^.+#[0-9]+$")]


class ProjectSummary(BaseModel):
    id: NonEmptyStr
    title: NonEmptyStr
    summary: str
    entry_chapter: NonEmptyStr
    updated_at: datetime


class ProjectListResponse(BaseModel):
    items: list[ProjectSummary]


class ProjectDetailResponse(BaseModel):
    id: NonEmptyStr
    title: NonEmptyStr
    summary: str
    entry_chapter: NonEmptyStr
    chapters: list[NonEmptyStr]
    scenario_revision: NonEmptyStr
    assets_base_url: NonEmptyStr


class LabelCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["label"]
    name: LabelPatternStr


class SayCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["say"]
    text: NonEmptyStr
    speaker: NonEmptyStr | None = None


class ChoiceOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: NonEmptyStr
    jump: LabelPatternStr


class ChoiceCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["choice"]
    options: Annotated[list[ChoiceOption], Field(min_length=1)]
    prompt: NonEmptyStr | None = None


class JumpCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["jump"]
    to: LabelPatternStr


ScalarValue = str | float | bool | None


class SetCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["set"]
    var: VariablePathStr
    value: ScalarValue
    op: Literal["assign", "add", "sub"] | None = None


class Condition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    var: VariablePathStr
    op: Literal["eq", "ne", "gt", "gte", "lt", "lte"]
    value: ScalarValue


class IfCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["if"]
    cond: Condition
    then: list["Command"]
    else_: list["Command"] | None = Field(default=None, alias="else")


Command = LabelCommand | SayCommand | ChoiceCommand | JumpCommand | SetCommand | IfCommand


class ScenarioV0(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: NonEmptyStr
    nodes: Annotated[list[Command], Field(min_length=1)]


class ScenarioChapterResponse(BaseModel):
    project_id: NonEmptyStr
    chapter_id: NonEmptyStr
    scenario: ScenarioV0
    warnings: list[str]


class ScenarioRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: NonEmptyStr
    revision: NonEmptyStr
    checksum: NonEmptyStr


class Position(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: NonEmptyStr
    index: Annotated[int, Field(ge=0)]


class LogEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    seq: Annotated[int, Field(ge=0)]
    kind: NonEmptyStr
    payload: dict


class ChoiceResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    at: HistoryEntryStr
    choice_id: NonEmptyStr
    selected_index: Annotated[int, Field(ge=0)]


class RngState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    seed: NonEmptyStr
    step: Annotated[int, Field(ge=0)]


class SaveDataV0(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state_version: Literal["0"]
    scenario_ref: ScenarioRef
    position: Position
    variables: dict[NonEmptyStr, ScalarValue]
    read_history: list[HistoryEntryStr]
    log: list[LogEntry]
    choice_results: list[ChoiceResult]
    rng: RngState


class SaveWriteResponse(BaseModel):
    project_id: NonEmptyStr
    slot: NonEmptyStr
    saved_at: datetime
