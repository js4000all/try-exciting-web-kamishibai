from copy import deepcopy

from app.engine import EnginePosition, EngineRng, EngineState, ScenarioCommandExecutor
from app.engine.save_codec import engine_state_from_save, save_from_engine_state
from app.saves import SaveDataV0


def test_branch_choice_reaches_terminal() -> None:
    scenario = {
        "id": "branching",
        "nodes": [
            {"type": "label", "name": "start"},
            {
                "type": "choice",
                "prompt": "Where to?",
                "options": [
                    {"text": "Go right", "jump": "right"},
                    {"text": "Go left", "jump": "left"},
                ],
            },
            {"type": "label", "name": "left"},
            {"type": "say", "text": "left end"},
            {"type": "jump", "to": "end"},
            {"type": "label", "name": "right"},
            {"type": "say", "text": "right end"},
            {"type": "jump", "to": "end"},
            {"type": "label", "name": "end"},
        ],
    }
    executor = ScenarioCommandExecutor()
    state = EngineState(position=EnginePosition(label="start", index=0), rng=EngineRng(seed="seed-1", step=0))

    prompt = executor.step(scenario, state)
    assert prompt.status == "awaiting_choice"

    selected = executor.step(scenario, state, choice_index=1)
    assert selected.status == "advanced"

    say = executor.step(scenario, state)
    assert say.status == "advanced"
    assert say.events[0].payload["text"] == "left end"

    finished = executor.step(scenario, state)
    assert finished.status == "finished"


def test_same_progress_after_save_and_load() -> None:
    scenario = {
        "id": "saveflow",
        "nodes": [
            {"type": "label", "name": "start"},
            {"type": "set", "var": "score", "op": "assign", "value": 10},
            {
                "type": "if",
                "cond": {"var": "score", "op": "gte", "value": 10},
                "then": [{"type": "jump", "to": "good"}],
                "else": [{"type": "jump", "to": "bad"}],
            },
            {"type": "label", "name": "bad"},
            {"type": "say", "text": "bad"},
            {"type": "jump", "to": "end"},
            {"type": "label", "name": "good"},
            {"type": "say", "text": "good"},
            {"type": "jump", "to": "end"},
            {"type": "label", "name": "end"},
        ],
    }
    executor = ScenarioCommandExecutor()
    state = EngineState(position=EnginePosition(label="start", index=0), rng=EngineRng(seed="seed-2", step=0))

    result_before_save = executor.step(scenario, state)
    assert result_before_save.status == "advanced"
    assert result_before_save.events[0].payload["text"] == "good"

    snapshot = deepcopy(state)
    save_data = save_from_engine_state(
        state=state,
        scenario_ref={"name": "project-1", "revision": "r1", "checksum": "c1"},
    )
    loaded_state = engine_state_from_save(SaveDataV0(**save_data.model_dump()))

    assert loaded_state.position == snapshot.position
    assert loaded_state.variables == snapshot.variables
    assert loaded_state.choice_results == snapshot.choice_results
    assert loaded_state.rng == snapshot.rng

    expected_after = executor.step(scenario, snapshot)
    actual_after = executor.step(scenario, loaded_state)
    assert actual_after.status == expected_after.status == "finished"
    assert loaded_state.position == snapshot.position
