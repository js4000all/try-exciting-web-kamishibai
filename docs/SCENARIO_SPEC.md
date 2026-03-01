# シナリオ仕様書

## 0. この文書の位置づけ（重要）

- **実装契約（必須/型/許容値）の正本は `server/schema/scenario-v0.schema.json`** とする。
- 本文書は、設計背景と v0 採用範囲を説明する補助資料であり、契約が衝突する場合は JSON Schema を優先する。

## 1. 設計思想（長期方針）

### 1.1 目的

ノベル実行機が読み込むシナリオの共通データモデルを統一し、将来的なフォーマット追加（JSON/YAML/DSL）を行ってもランタイムの実装再利用を可能にする。

### 1.2 レイヤ分離

- 入力レイヤ: YAML / JSON / DSL などの記法差を吸収
- 実行レイヤ: 命令列として同一形式で解釈
- 検証レイヤ: JSON Schema による構造検証 + 実行機側の意味検証

### 1.3 v0 の割り切り

v0 では「実装可能性」と「検証容易性」を優先し、命令を最小集合に限定する。演出系命令（背景/音声/待機など）は将来拡張で扱う。

## 2. v0 採用サブセット（実装対象）

### 2.1 命令一覧

- `label`
- `say`
- `choice`
- `jump`
- `set`
- `if`

### 2.2 実装上の期待動作

- `nodes` は先頭から順に評価する。
- `label` は現在位置に名前を付与する（副作用なし）。
- `choice` / `jump` / `if` は制御フローを変更する。
- `set` は変数ストアを更新する。
- `if` の `then`/`else` は入れ子命令列として逐次実行する。

> 具体フィールド（必須/任意）や型、正規表現、enum は `server/schema/scenario-v0.schema.json` を参照。

## 3. v0 でスキーマ外に扱う検証

以下は JSON Schema だけでは担保しないため、実行機または専用バリデータで検証する。

- `jump` / `choice.options[*].jump` の参照先ラベル存在確認
- 到達不能ラベルや無限ループなどの実行可能性チェック
- 変数名規約・シナリオ運用上の lint

## 4. 参考

- スキーマ本体: `server/schema/scenario-v0.schema.json`
- 仕様補助: `shared/specs/scenario-format-v0.md`
- 正例: `server/schema/examples/scenario.valid.json`
