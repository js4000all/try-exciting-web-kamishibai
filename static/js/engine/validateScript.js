function asObject(value) {
  return value != null && typeof value === "object" && !Array.isArray(value);
}

export function validateScript(script) {
  if (!Array.isArray(script)) {
    throw new Error("script はコマンド配列である必要があります。");
  }

  const labels = new Map();
  const errors = [];

  for (let i = 0; i < script.length; i += 1) {
    const cmd = script[i];

    if (!asObject(cmd)) {
      errors.push(`[${i}] コマンドはオブジェクトである必要があります。`);
      continue;
    }

    if ("label" in cmd) {
      if (typeof cmd.label !== "string" || cmd.label.length === 0) {
        errors.push(`[${i}] label は空でない文字列で指定してください。`);
      } else if (labels.has(cmd.label)) {
        errors.push(`[${i}] label "${cmd.label}" が重複しています（先に [${labels.get(cmd.label)}] で定義）。`);
      } else {
        labels.set(cmd.label, i);
      }
    }

    if ("choice" in cmd) {
      if (!Array.isArray(cmd.choice)) {
        errors.push(`[${i}] choice は配列で指定してください。`);
      } else {
        cmd.choice.forEach((choice, choiceIndex) => {
          if (!asObject(choice)) {
            errors.push(`[${i}] choice[${choiceIndex}] はオブジェクトである必要があります。`);
            return;
          }

          if (typeof choice.text !== "string" || choice.text.length === 0) {
            errors.push(`[${i}] choice[${choiceIndex}].text は必須の文字列です。`);
          }
        });
      }
    }
  }

  const isDefinedLabel = (label) => typeof label === "string" && labels.has(label);

  for (let i = 0; i < script.length; i += 1) {
    const cmd = script[i];
    if (!asObject(cmd)) continue;

    if ("jump" in cmd && !isDefinedLabel(cmd.jump)) {
      errors.push(`[${i}] jump 先ラベル "${cmd.jump}" が未定義です。`);
    }

    if (cmd.jumpIf && !isDefinedLabel(cmd.jumpIf.to)) {
      errors.push(`[${i}] jumpIf.to ラベル "${cmd.jumpIf.to}" が未定義です。`);
    }

    if (Array.isArray(cmd.choice)) {
      cmd.choice.forEach((choice, choiceIndex) => {
        if (asObject(choice) && "jump" in choice && !isDefinedLabel(choice.jump)) {
          errors.push(`[${i}] choice[${choiceIndex}].jump ラベル "${choice.jump}" が未定義です。`);
        }
      });
    }
  }

  return errors;
}
