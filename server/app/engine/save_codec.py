from __future__ import annotations

from app.engine.types import EngineChoiceResult, EnginePosition, EngineRng, EngineState
from app.saves import ChoiceResult, Position, RngState, SaveDataV0, ScenarioRef


def engine_state_from_save(save_data: SaveDataV0) -> EngineState:
    return EngineState(
        position=EnginePosition(
            label=save_data.position.label,
            index=save_data.position.index,
        ),
        variables=dict(save_data.variables),
        choice_results=[
            EngineChoiceResult(
                at=item.at,
                choice_id=item.choice_id,
                selected_index=item.selected_index,
            )
            for item in save_data.choice_results
        ],
        rng=EngineRng(seed=save_data.rng.seed, step=save_data.rng.step),
    )


def save_from_engine_state(
    *,
    state: EngineState,
    scenario_ref: ScenarioRef,
    read_history: list[str] | None = None,
    log: list[dict] | None = None,
) -> SaveDataV0:
    return SaveDataV0(
        state_version="0",
        scenario_ref=scenario_ref,
        position=Position(label=state.position.label, index=state.position.index),
        variables=dict(state.variables),
        read_history=read_history or [],
        log=log or [],
        choice_results=[
            ChoiceResult(
                at=item.at,
                choice_id=item.choice_id,
                selected_index=item.selected_index,
            )
            for item in state.choice_results
        ],
        rng=RngState(seed=state.rng.seed, step=state.rng.step),
    )
