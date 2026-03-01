from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

ScalarValue = str | int | float | bool | None


@dataclass(slots=True)
class EnginePosition:
    label: str
    index: int


@dataclass(slots=True)
class EngineChoiceResult:
    at: str
    choice_id: str
    selected_index: int


@dataclass(slots=True)
class EngineRng:
    seed: str
    step: int


@dataclass(slots=True)
class EngineState:
    position: EnginePosition
    variables: dict[str, ScalarValue] = field(default_factory=dict)
    choice_results: list[EngineChoiceResult] = field(default_factory=list)
    rng: EngineRng = field(default_factory=lambda: EngineRng(seed="default", step=0))


@dataclass(slots=True)
class EngineEvent:
    kind: str
    payload: dict[str, Any]


@dataclass(slots=True)
class StepResult:
    status: Literal["advanced", "awaiting_choice", "finished"]
    state: EngineState
    events: list[EngineEvent] = field(default_factory=list)


class CommandExecutor(Protocol):
    def step(
        self,
        scenario: dict[str, Any],
        state: EngineState,
        *,
        choice_index: int | None = None,
    ) -> StepResult: ...
