export function createRuntime({ script, renderer }) {
  const state = {
    idx: 0,
    labels: new Map(),
    flags: {},
  };

  script.forEach((cmd, i) => {
    if (cmd.label) state.labels.set(cmd.label, i);
  });

  function jumpTo(label) {
    const pos = state.labels.get(label);
    if (pos == null) return;
    state.idx = pos;
  }

  function apply(cmd) {
    if (cmd.bg || cmd.bgColor) renderer.setBackground(cmd);

    if ("leftOn" in cmd || cmd.left) {
      renderer.setCharacter("left", { on: !!cmd.leftOn, url: cmd.left });
    }
    if ("rightOn" in cmd || cmd.right) {
      renderer.setCharacter("right", { on: !!cmd.rightOn, url: cmd.right });
    }

    if ("name" in cmd) renderer.setName(cmd.name ?? "");
    if ("text" in cmd) renderer.setText(cmd.text ?? "");

    if (cmd.set) Object.assign(state.flags, cmd.set);

    if (cmd.jumpIf) {
      const { key, equals, to } = cmd.jumpIf;
      if ((state.flags[key] ?? false) === equals) jumpTo(to);
    }

    if (cmd.choice) {
      renderer.showChoices(cmd.choice, (choice) => {
        if (choice.set) Object.assign(state.flags, choice.set);
        if (choice.jump) jumpTo(choice.jump);
        next();
      });
      return "WAIT_CHOICE";
    }

    if (cmd.jump) jumpTo(cmd.jump);

    return "CONTINUE";
  }

  function next() {
    renderer.clearChoices();

    while (state.idx < script.length) {
      const cmd = script[state.idx++];
      if (cmd.label) continue;
      const result = apply(cmd);
      if (result === "WAIT_CHOICE") return;
      if ("text" in cmd || "name" in cmd) return;
    }

    renderer.setName("");
    renderer.setText("（おしまい）");
  }

  return {
    next,
    apply,
    jumpTo,
    get state() {
      return state;
    },
  };
}
