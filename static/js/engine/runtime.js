import { parseScenarioScript } from "./parseScenario.js";
import { validateScript } from "./validateScript.js";

const STATUS = {
  CONTINUE: "CONTINUE",
  WAIT_CHOICE: "WAIT_CHOICE",
  DONE: "DONE",
};

export function createRuntime({ script, renderer }) {
  const errors = validateScript(script);
  if (errors.length > 0) {
    throw new Error(`スクリプト検証エラー:\n${errors.join("\n")}`);
  }

  const scenario = parseScenarioScript(script);

  const state = {
    idx: 0,
    labels: scenario.labels,
    flags: {},
    status: STATUS.CONTINUE,
    dialogue: { name: "", text: "" },
  };

  function jumpTo(label) {
    const pos = state.labels.get(label);
    if (pos == null) return;
    state.idx = pos;
  }

  function applyAction(action) {
    if (action.type === "BACKGROUND") {
      renderer.setBackground(action);
      return STATUS.CONTINUE;
    }

    if (action.type === "CHARACTER") {
      renderer.setCharacter(action.side, { on: action.on, url: action.url });
      return STATUS.CONTINUE;
    }

    if (action.type === "DIALOGUE") {
      if (action.hasName) state.dialogue.name = action.name;
      if (action.hasText) state.dialogue.text = action.text;
      renderer.setDialogue(state.dialogue);
      return STATUS.CONTINUE;
    }

    if (action.type === "SET_FLAGS") {
      Object.assign(state.flags, action.value);
      return STATUS.CONTINUE;
    }

    if (action.type === "JUMP_IF") {
      if ((state.flags[action.key] ?? false) === action.equals) jumpTo(action.to);
      return STATUS.CONTINUE;
    }

    if (action.type === "CHOICE") {
      renderer.showChoices(action.options, (choice) => {
        if (choice.set) Object.assign(state.flags, choice.set);
        if (choice.jump) jumpTo(choice.jump);
        state.status = STATUS.CONTINUE;
        next();
      });
      state.status = STATUS.WAIT_CHOICE;
      return STATUS.WAIT_CHOICE;
    }

    if (action.type === "JUMP") {
      jumpTo(action.to);
    }

    return STATUS.CONTINUE;
  }

  function apply(instruction) {
    if (instruction.type !== "STEP") return STATUS.CONTINUE;

    for (const action of instruction.actions) {
      const result = applyAction(action);
      if (result === STATUS.WAIT_CHOICE) return STATUS.WAIT_CHOICE;
    }

    return STATUS.CONTINUE;
  }

  function next() {
    if (state.status === STATUS.DONE) return;

    renderer.showChoices([], () => {});

    while (state.idx < scenario.instructions.length) {
      const instruction = scenario.instructions[state.idx++];
      if (instruction.type === "LABEL") continue;
      const result = apply(instruction);
      if (result === STATUS.WAIT_CHOICE) return;
      if (instruction.actions.some((action) => action.type === "DIALOGUE")) {
        state.status = STATUS.CONTINUE;
        return;
      }
    }

    state.dialogue.name = "";
    state.dialogue.text = "（おしまい）";
    renderer.setDialogue(state.dialogue);
    state.status = STATUS.DONE;
  }

  return {
    next,
    apply,
    jumpTo,
    get state() {
      return state;
    },
    get status() {
      return state.status;
    },
    STATUS,
  };
}
