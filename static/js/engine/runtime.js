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

  const state = {
    idx: 0,
    labels: new Map(),
    flags: {},
    status: STATUS.CONTINUE,
    dialogue: { name: "", text: "" },
  };

  script.forEach((cmd, i) => {
    if (cmd.label) state.labels.set(cmd.label, i);
  });

  function jumpTo(label) {
    const pos = state.labels.get(label);
    if (pos == null) return;
    state.idx = pos;
  }

  function updateDialogue(cmd) {
    if ("name" in cmd) state.dialogue.name = cmd.name ?? "";
    if ("text" in cmd) state.dialogue.text = cmd.text ?? "";

    if ("name" in cmd || "text" in cmd) {
      renderer.setDialogue(state.dialogue);
    }
  }

  function apply(cmd) {
    if (cmd.bg || cmd.bgColor) renderer.setBackground(cmd);

    if ("leftOn" in cmd || cmd.left) {
      renderer.setCharacter("left", { on: !!cmd.leftOn, url: cmd.left });
    }
    if ("rightOn" in cmd || cmd.right) {
      renderer.setCharacter("right", { on: !!cmd.rightOn, url: cmd.right });
    }

    updateDialogue(cmd);

    if (cmd.set) Object.assign(state.flags, cmd.set);

    if (cmd.jumpIf) {
      const { key, equals, to } = cmd.jumpIf;
      if ((state.flags[key] ?? false) === equals) jumpTo(to);
    }

    if (cmd.choice) {
      renderer.showChoices(cmd.choice, (choice) => {
        if (choice.set) Object.assign(state.flags, choice.set);
        if (choice.jump) jumpTo(choice.jump);
        state.status = STATUS.CONTINUE;
        next();
      });
      state.status = STATUS.WAIT_CHOICE;
      return STATUS.WAIT_CHOICE;
    }

    if (cmd.jump) jumpTo(cmd.jump);

    return STATUS.CONTINUE;
  }

  function next() {
    if (state.status === STATUS.DONE) return;

    renderer.showChoices([], () => {});

    while (state.idx < script.length) {
      const cmd = script[state.idx++];
      if (cmd.label) continue;
      const result = apply(cmd);
      if (result === STATUS.WAIT_CHOICE) return;
      if ("text" in cmd || "name" in cmd) {
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
