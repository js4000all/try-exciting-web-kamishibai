import { useEffect, useState } from "react";

import { ApiError, apiClient } from "./api/client";
import type { SaveDataV0 } from "./api/client";

type SetOp = "assign" | "add" | "sub";
type SetValue = string | number | boolean | null;

type LabelCommand = { type: "label"; name: string };
type SayCommand = { type: "say"; speaker?: string; text: string };
type ChoiceOption = { text: string; jump: string };
type ChoiceCommand = { type: "choice"; prompt?: string; options: [ChoiceOption, ...ChoiceOption[]] };
type JumpCommand = { type: "jump"; to: string };
type SetCommand = { type: "set"; var: string; op?: SetOp; value: SetValue };
type IfCommand = { type: "if"; cond: { var: string; op: "eq" | "ne" | "gt" | "gte" | "lt" | "lte"; value: SetValue }; then: Command[]; else?: Command[] };
type Command = LabelCommand | SayCommand | ChoiceCommand | JumpCommand | SetCommand | IfCommand;
type ScenarioV0 = { id: string; nodes: [Command, ...Command[]] };

type EngineView =
  | { kind: "say"; speaker?: string; text: string }
  | { kind: "choice"; prompt?: string; options: ChoiceOption[] }
  | { kind: "finished" };

type RuntimeState = {
  index: number;
  label: string;
  variables: Record<string, SetValue>;
  choiceResults: Array<{ at: string; choice_id: string; selected_index: number }>;
};

const SLOT = "1";

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function toScenario(raw: unknown): ScenarioV0 {
  if (!isObject(raw) || !Array.isArray(raw.nodes) || typeof raw.id !== "string") {
    throw new Error("Scenario payload is invalid");
  }
  return raw as unknown as ScenarioV0;
}

function executeUntilInteractive(
  scenario: ScenarioV0,
  prev: RuntimeState,
  selectedChoiceIndex?: number,
): { state: RuntimeState; view: EngineView } {
  const nodes = scenario.nodes;
  const next: RuntimeState = {
    index: prev.index,
    label: prev.label,
    variables: { ...prev.variables },
    choiceResults: [...prev.choiceResults],
  };

  for (let guard = 0; guard < 1000; guard += 1) {
    const command = nodes[next.index];
    if (!command) {
      return { state: next, view: { kind: "finished" } };
    }

    const result = executeCommand({ scenarioId: scenario.id, nodes, state: next, command, selectedChoiceIndex });
    if (result === null) {
      continue;
    }
    return { state: next, view: result };
  }

  return { state: next, view: { kind: "finished" } };
}

function findLabelIndex(nodes: Command[], label: string): number {
  const found = nodes.findIndex((node) => node.type === "label" && node.name === label);
  return found >= 0 ? found : nodes.length;
}

function executeCommand(params: {
  scenarioId: string;
  nodes: Command[];
  state: RuntimeState;
  command: Command;
  selectedChoiceIndex?: number;
}): EngineView | null {
  const { scenarioId, nodes, state, command, selectedChoiceIndex } = params;

  if (command.type === "label") {
    state.label = command.name;
    state.index += 1;
    return null;
  }

  if (command.type === "jump") {
    state.label = command.to;
    state.index = findLabelIndex(nodes, command.to);
    return null;
  }

  if (command.type === "set") {
    const op = command.op ?? "assign";
    const current = state.variables[command.var];
    if (op === "assign") {
      state.variables[command.var] = command.value;
    }
    if (op === "add" && typeof current === "number" && typeof command.value === "number") {
      state.variables[command.var] = current + command.value;
    }
    if (op === "sub" && typeof current === "number" && typeof command.value === "number") {
      state.variables[command.var] = current - command.value;
    }
    state.index += 1;
    return null;
  }

  if (command.type === "say") {
    state.index += 1;
    return { kind: "say", speaker: command.speaker, text: command.text };
  }

  if (command.type === "choice") {
    if (selectedChoiceIndex === undefined) {
      return { kind: "choice", prompt: command.prompt, options: [...command.options] };
    }

    const option = command.options[selectedChoiceIndex];
    if (!option) {
      return { kind: "choice", prompt: command.prompt, options: [...command.options] };
    }

    state.choiceResults.push({
      at: `${scenarioId}#${state.index}`,
      choice_id: `choice-${state.index}`,
      selected_index: selectedChoiceIndex,
    });

    state.label = option.jump;
    state.index = findLabelIndex(nodes, option.jump);
    return null;
  }

  if (command.type === "if") {
    state.index += 1;
    return null;
  }

  return null;
}

function buildSaveData(projectId: string, revision: string, state: RuntimeState): SaveDataV0 {
  return {
    state_version: "0",
    scenario_ref: {
      name: projectId,
      revision,
      checksum: "local",
    },
    position: {
      label: state.label,
      index: state.index,
    },
    variables: state.variables,
    read_history: [],
    log: [],
    choice_results: state.choiceResults,
    rng: {
      seed: "local",
      step: 0,
    },
  };
}

export function App() {
  const [projectId, setProjectId] = useState<string>("");
  const [scenarioRevision, setScenarioRevision] = useState<string>("0");
  const [scenario, setScenario] = useState<ScenarioV0 | null>(null);
  const [runtime, setRuntime] = useState<RuntimeState>({ index: 0, label: "start", variables: {}, choiceResults: [] });
  const [view, setView] = useState<EngineView>({ kind: "finished" });
  const [lastApiState, setLastApiState] = useState<unknown>(null);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const projects = await apiClient.getProjects();
        const first = projects.items[0];
        if (!first) {
          return;
        }

        const detail = await apiClient.getProject(first.id);
        const chapter = await apiClient.getChapterScenario(first.id, detail.entry_chapter);
        const scenarioData = toScenario(chapter.scenario);
        const initialRuntime: RuntimeState = { index: 0, label: "start", variables: {}, choiceResults: [] };
        const execution = executeUntilInteractive(scenarioData, initialRuntime);

        setProjectId(first.id);
        setScenarioRevision(detail.scenario_revision);
        setScenario(scenarioData);
        setRuntime(execution.state);
        setView(execution.view);
        setLastApiState(chapter);
      } catch (caught) {
        if (caught instanceof ApiError) {
          setError(caught);
        }
      }
    };

    void load();
  }, []);

  const onNext = () => {
    if (!scenario) {
      return;
    }
    const execution = executeUntilInteractive(scenario, runtime);
    setRuntime(execution.state);
    setView(execution.view);
  };

  const onChoice = (choiceIndex: number) => {
    if (!scenario) {
      return;
    }
    const execution = executeUntilInteractive(scenario, runtime, choiceIndex);
    setRuntime(execution.state);
    setView(execution.view);
  };

  const onSave = async () => {
    if (!projectId) {
      return;
    }
    try {
      const response = await apiClient.save(projectId, SLOT, buildSaveData(projectId, scenarioRevision, runtime));
      setLastApiState(response);
      setError(null);
    } catch (caught) {
      if (caught instanceof ApiError) {
        setError(caught);
      }
    }
  };

  const onLoad = async () => {
    if (!projectId || !scenario) {
      return;
    }
    try {
      const response = await apiClient.load(projectId, SLOT);
      const loadedRuntime: RuntimeState = {
        index: response.data.position.index,
        label: response.data.position.label,
        variables: response.data.variables,
        choiceResults: response.data.choice_results ?? [],
      };
      const execution = executeUntilInteractive(scenario, loadedRuntime);
      setRuntime(execution.state);
      setView(execution.view);
      setLastApiState(response);
      setError(null);
    } catch (caught) {
      if (caught instanceof ApiError) {
        setError(caught);
      }
    }
  };

  return (
    <main style={{ maxWidth: 720, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1>Kamishibai v0</h1>

      {error?.code === "RESOURCE_NOT_FOUND" ? (
        <p style={{ color: "crimson" }}>Not found: {error.message}</p>
      ) : null}
      {error?.code === "VALIDATION_ERROR" ? (
        <p style={{ color: "darkorange" }}>Validation error: {error.message}</p>
      ) : null}
      {error && error.code !== "RESOURCE_NOT_FOUND" && error.code !== "VALIDATION_ERROR" ? (
        <p style={{ color: "crimson" }}>{error.message}</p>
      ) : null}

      <section>
        <h2>現在テキスト</h2>
        {view.kind === "say" ? <p>{view.speaker ? `${view.speaker}: ` : ""}{view.text}</p> : null}
        {view.kind === "finished" ? <p>End</p> : null}
      </section>

      <section style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        {view.kind === "choice"
          ? view.options.map((option, index) => (
              <button key={`${option.text}-${index}`} onClick={() => onChoice(index)} type="button">
                {option.text}
              </button>
            ))
          : null}
      </section>

      <section style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button onClick={onNext} type="button" disabled={view.kind !== "say"}>
          次へ
        </button>
        <button onClick={onSave} type="button">
          Save
        </button>
        <button onClick={onLoad} type="button">
          Load
        </button>
      </section>

      <h3>API/実行状態</h3>
      <pre>{JSON.stringify({ runtime, view, lastApiState }, null, 2)}</pre>
    </main>
  );
}
