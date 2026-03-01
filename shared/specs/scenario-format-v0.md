# Scenario Format v0

この文書は `server/schema/scenario-v0.schema.json` の補助説明です。**実装契約は常に JSON Schema を正**とし、ここでは v0 で採用する最小命令セット（`say` / `choice` / `jump` / `set` / `if` / `label`）を読みやすく要約します。

## 1. ルート構造

```json
{
  "id": "main_story",
  "nodes": [
    { "type": "label", "name": "start" },
    { "type": "say", "speaker": "Narrator", "text": "はじまり" }
  ]
}
```

- `id`: シナリオ識別子（空文字不可）
- `nodes`: 命令配列（1件以上）

## 2. 命令フォーマット

### `label`

```json
{ "type": "label", "name": "start" }
```

- `name`: ラベル名（`^[A-Za-z_][A-Za-z0-9_-]*$`）

### `say`

```json
{ "type": "say", "speaker": "Guide", "text": "右に進みますか？" }
```

- 必須: `text`
- 任意: `speaker`

### `choice`

```json
{
  "type": "choice",
  "prompt": "どうする？",
  "options": [
    { "text": "右へ", "jump": "go_right" },
    { "text": "左へ", "jump": "go_left" }
  ]
}
```

- 必須: `options`（1件以上）
- 任意: `prompt`
- `options[*].jump`: 遷移先ラベル名

### `jump`

```json
{ "type": "jump", "to": "ending" }
```

- `to`: 遷移先ラベル名

### `set`

```json
{ "type": "set", "var": "flags.seen_intro", "op": "assign", "value": true }
```

- 必須: `var`, `value`
- 任意: `op`（`assign` / `add` / `sub`）

### `if`

```json
{
  "type": "if",
  "cond": { "var": "state.score", "op": "gte", "value": 10 },
  "then": [{ "type": "jump", "to": "good_end" }],
  "else": [{ "type": "jump", "to": "normal_end" }]
}
```

- 必須: `cond`, `then`
- 任意: `else`
- 条件演算子: `eq` / `ne` / `gt` / `gte` / `lt` / `lte`

## 3. 補足

- スキーマは各命令で `additionalProperties: false` を採用しており、未定義キーは不許可です。
- ラベルの存在確認や到達可能性などの**意味的検証**は、スキーマ外で実行機/検証ツールが担います。
