function asObject(value) {
  return value != null && typeof value === "object" && !Array.isArray(value);
}

function toFlagRecord(value) {
  return asObject(value) ? { ...value } : {};
}

function toChoiceOption(choice) {
  return {
    text: choice.text,
    set: toFlagRecord(choice.set),
    jump: typeof choice.jump === "string" ? choice.jump : null,
  };
}

export function parseScenarioScript(script) {
  if (!Array.isArray(script)) {
    throw new Error("script はコマンド配列である必要があります。");
  }

  const instructions = [];
  const labels = new Map();

  for (let i = 0; i < script.length; i += 1) {
    const cmd = script[i];

    if (!asObject(cmd)) {
      throw new Error(`script[${i}] はオブジェクトである必要があります。`);
    }

    if ("label" in cmd) {
      if (typeof cmd.label !== "string" || cmd.label.length === 0) {
        throw new Error(`script[${i}].label は空でない文字列で指定してください。`);
      }

      labels.set(cmd.label, instructions.length);
      instructions.push({
        type: "LABEL",
        sourceIndex: i,
        label: cmd.label,
      });
      continue;
    }

    const actions = [];

    if (cmd.bg || cmd.bgColor) {
      actions.push({
        type: "BACKGROUND",
        bg: typeof cmd.bg === "string" ? cmd.bg : null,
        bgColor: typeof cmd.bgColor === "string" ? cmd.bgColor : null,
      });
    }

    if ("leftOn" in cmd || "left" in cmd) {
      actions.push({
        type: "CHARACTER",
        side: "left",
        on: !!cmd.leftOn,
        url: typeof cmd.left === "string" ? cmd.left : null,
      });
    }

    if ("rightOn" in cmd || "right" in cmd) {
      actions.push({
        type: "CHARACTER",
        side: "right",
        on: !!cmd.rightOn,
        url: typeof cmd.right === "string" ? cmd.right : null,
      });
    }

    if ("name" in cmd || "text" in cmd) {
      actions.push({
        type: "DIALOGUE",
        hasName: "name" in cmd,
        hasText: "text" in cmd,
        name: cmd.name ?? "",
        text: cmd.text ?? "",
      });
    }

    if (cmd.set) {
      actions.push({
        type: "SET_FLAGS",
        value: toFlagRecord(cmd.set),
      });
    }

    if (cmd.jumpIf) {
      actions.push({
        type: "JUMP_IF",
        key: cmd.jumpIf.key,
        equals: cmd.jumpIf.equals,
        to: cmd.jumpIf.to,
      });
    }

    if (Array.isArray(cmd.choice)) {
      actions.push({
        type: "CHOICE",
        options: cmd.choice.map(toChoiceOption),
      });
    }

    if ("jump" in cmd) {
      actions.push({
        type: "JUMP",
        to: cmd.jump,
      });
    }

    instructions.push({
      type: "STEP",
      sourceIndex: i,
      actions,
    });
  }

  return { instructions, labels };
}
