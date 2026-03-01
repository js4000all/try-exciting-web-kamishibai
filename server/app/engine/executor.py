from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.engine.types import CommandExecutor, EngineChoiceResult, EngineEvent, EngineState, StepResult


class ScenarioCommandExecutor(CommandExecutor):
    def step(
        self,
        scenario: dict[str, Any],
        state: EngineState,
        *,
        choice_index: int | None = None,
    ) -> StepResult:
        nodes = scenario["nodes"]
        labels = _label_index(nodes)

        while True:
            if state.position.index >= len(nodes):
                return StepResult(status="finished", state=state, events=[])

            command = nodes[state.position.index]
            result = _execute_command(
                command=command,
                state=state,
                labels=labels,
                scenario_id=scenario["id"],
                choice_index=choice_index,
            )
            if result is None:
                continue
            return result


def _execute_command(
    *,
    command: dict[str, Any],
    state: EngineState,
    labels: dict[str, int],
    scenario_id: str,
    choice_index: int | None,
) -> StepResult | None:
    command_type = command["type"]

    if command_type == "label":
        state.position.label = command["name"]
        state.position.index += 1
        return None

    if command_type == "jump":
        state.position.label = command["to"]
        state.position.index = labels[command["to"]]
        return None

    if command_type == "set":
        _apply_set(state.variables, command)
        state.position.index += 1
        return None

    if command_type == "if":
        branch = command["then"] if _eval_condition(state.variables, command["cond"]) else command.get("else", [])
        state.position.index += 1
        events: list[EngineEvent] = []
        for branch_command in branch:
            branch_result = _execute_inline_command(
                command=branch_command,
                state=state,
                labels=labels,
                scenario_id=scenario_id,
                choice_index=choice_index,
            )
            if branch_result is not None:
                branch_result.events = events + branch_result.events
                return branch_result
        return None

    if command_type == "say":
        state.position.index += 1
        return StepResult(
            status="advanced",
            state=state,
            events=[
                EngineEvent(
                    kind="io.say",
                    payload={"speaker": command.get("speaker"), "text": command["text"]},
                )
            ],
        )

    if command_type == "choice":
        if choice_index is None:
            return StepResult(
                status="awaiting_choice",
                state=state,
                events=[
                    EngineEvent(
                        kind="io.choice_prompt",
                        payload={
                            "prompt": command.get("prompt"),
                            "options": deepcopy(command["options"]),
                        },
                    )
                ],
            )

        if choice_index < 0 or choice_index >= len(command["options"]):
            raise ValueError("choice_index is out of range")

        selected = command["options"][choice_index]
        state.choice_results.append(
            EngineChoiceResult(
                at=f"{scenario_id}#{state.position.index}",
                choice_id=f"choice-{state.position.index}",
                selected_index=choice_index,
            )
        )
        state.position.label = selected["jump"]
        state.position.index = labels[selected["jump"]]
        return StepResult(
            status="advanced",
            state=state,
            events=[
                EngineEvent(
                    kind="io.choice_selected",
                    payload={"selected_index": choice_index, "jump": selected["jump"]},
                )
            ],
        )

    raise ValueError(f"Unsupported command type: {command_type}")


def _execute_inline_command(
    *,
    command: dict[str, Any],
    state: EngineState,
    labels: dict[str, int],
    scenario_id: str,
    choice_index: int | None,
) -> StepResult | None:
    command_type = command["type"]
    if command_type == "label":
        state.position.label = command["name"]
        return None
    if command_type == "jump":
        state.position.label = command["to"]
        state.position.index = labels[command["to"]]
        return None
    if command_type == "set":
        _apply_set(state.variables, command)
        return None
    if command_type == "if":
        branch = command["then"] if _eval_condition(state.variables, command["cond"]) else command.get("else", [])
        for branch_command in branch:
            nested = _execute_inline_command(
                command=branch_command,
                state=state,
                labels=labels,
                scenario_id=scenario_id,
                choice_index=choice_index,
            )
            if nested is not None:
                return nested
        return None
    if command_type == "say":
        return StepResult(
            status="advanced",
            state=state,
            events=[EngineEvent(kind="io.say", payload={"speaker": command.get("speaker"), "text": command["text"]})],
        )
    if command_type == "choice":
        if choice_index is None:
            return StepResult(
                status="awaiting_choice",
                state=state,
                events=[EngineEvent(kind="io.choice_prompt", payload={"prompt": command.get("prompt"), "options": deepcopy(command["options"])})],
            )
        selected = command["options"][choice_index]
        state.choice_results.append(
            EngineChoiceResult(
                at=f"{scenario_id}#{state.position.index}",
                choice_id=f"choice-{state.position.index}",
                selected_index=choice_index,
            )
        )
        state.position.label = selected["jump"]
        state.position.index = labels[selected["jump"]]
        return None
    raise ValueError(f"Unsupported command type: {command_type}")


def _label_index(nodes: list[dict[str, Any]]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for idx, node in enumerate(nodes):
        if node["type"] == "label":
            mapping[node["name"]] = idx
    return mapping


def _apply_set(variables: dict[str, Any], command: dict[str, Any]) -> None:
    name = command["var"]
    value = command["value"]
    op = command.get("op", "assign")
    current = variables.get(name, 0)

    if op == "assign":
        variables[name] = value
    elif op == "add":
        variables[name] = current + value
    elif op == "sub":
        variables[name] = current - value
    else:
        raise ValueError(f"Unsupported set op: {op}")


def _eval_condition(variables: dict[str, Any], cond: dict[str, Any]) -> bool:
    left = variables.get(cond["var"])
    right = cond["value"]
    op = cond["op"]

    if op == "eq":
        return left == right
    if op == "ne":
        return left != right
    if op == "gt":
        return left is not None and left > right
    if op == "gte":
        return left is not None and left >= right
    if op == "lt":
        return left is not None and left < right
    if op == "lte":
        return left is not None and left <= right
    raise ValueError(f"Unsupported condition op: {op}")
