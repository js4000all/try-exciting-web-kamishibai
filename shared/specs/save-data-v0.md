# セーブデータ / 状態モデル仕様 v0

本仕様は `shared/` で扱う状態モデル（実行状態および保存データ）の最小契約を定義する。
対象は `server/` の実行機と `web/` の描画レイヤーであり、両者は本仕様に準拠したデータを読み書きする。

## 1. 将来拡張（先行定義）

- 本仕様の互換管理キーとして `state_version` を必須とする。
- v0 の `state_version` は固定値 `"0"` とする。
- 将来バージョン（v1+）への移行時は、**読み込み時マイグレーション**を基本方針とする。
  - 旧バージョン入力を受け取った実装は、最新内部表現へ正規化してから実行を開始する。
  - マイグレーション不能なデータは、破損扱いとして明示エラーを返す。
- 互換性ルール:
  - 同一 `state_version` 内では後方互換を維持する。
  - 破壊的変更は新しい `state_version` を採番してのみ許可する。

## 2. 位置情報モデル（`label + index`）

状態の現在位置は、次の 2 要素で保持する。

- `label: string`
  - シナリオ内の論理ブロック識別子。
- `index: integer`
  - 当該 `label` 内で次に評価する命令の 0 始まり位置。

`position` は以下を満たすこと。

- `position.label` は空文字列不可。
- `position.index` は `>= 0`。
- `position` の正当性（`label` 存在、`index` 範囲内）はシナリオ定義と照合して検証する。

```json
{
  "position": {
    "label": "intro",
    "index": 3
  }
}
```

## 3. 状態データ構造

### 3.1 変数ストア（キー/値型）

`variables` は文字列キーの連想配列とする。

- キー: `string`（空文字列不可）
- 値型（v0 で許可）:
  - `string`
  - `number`（JSON Number）
  - `boolean`
  - `null`

```json
{
  "variables": {
    "player_name": "Aoi",
    "affinity": 12,
    "met_guide": true,
    "last_seen": null
  }
}
```

### 3.2 既読履歴

`read_history` は既読命令の集合を保持する。

- 型: `string[]`
- 各要素形式: `"<label>#<index>"`
- 同一要素の重複は不可。

実装上は高速化のため set 扱いを推奨するが、保存形式は JSON 配列とする。

### 3.3 ログ

`log` は表示・実行の追跡用レコード配列とする。

- 型: `LogEntry[]`
- `LogEntry`:
  - `seq: integer`（0 始まり単調増加）
  - `kind: string`（例: `line`, `choice`, `system`）
  - `payload: object`（kind ごとの拡張データ）

最低限、保存/復元再現に不要なログは省略可能だが、保持する場合は順序保証を行う。

### 3.4 選択結果

`choice_results` は選択肢入力の確定履歴を保持する。

- 型: `ChoiceResult[]`
- `ChoiceResult`:
  - `at: string`（`"<label>#<index>"`）
  - `choice_id: string`（シナリオ定義側の選択肢識別子）
  - `selected_index: integer`（表示順の 0 始まり）

同一 `at` に複数結果を保持する場合は時系列末尾を最新として扱う。

## 4. ランダム要素のシード管理方針

再現性維持のため、乱数利用時は以下を必須とする。

- `rng.seed: string`
  - セーブ開始時（または新規ゲーム開始時）に固定されるシード値。
- `rng.step: integer`
  - 乱数生成器の消費回数（0 始まり）。

復元後は `seed` と `step` から乱数状態を再構築し、次の乱数結果が保存前連続実行時と一致しなければならない。

```json
{
  "rng": {
    "seed": "project-1-slot-2-20250101",
    "step": 14
  }
}
```

## 5. シナリオ同一性検証（識別子 + チェックサム）

保存時と復元時で参照するシナリオ内部モデルが同一であることを検証するため、
セーブデータにはシナリオ識別情報を保持する。

- `scenario_ref.name: string`
  - ユーザー向け表示名（または論理名）。
- `scenario_ref.revision: string`
  - 実装側が管理するバージョン識別子（例: git commit, build id）。
- `scenario_ref.checksum: string`
  - 実行対象となる正規化済みシナリオ内部モデルに対するハッシュ値。
  - 推奨: SHA-256（hex）。

### 5.1 ロード時判定ポリシー（UX 指針）

実際の UX が「シナリオ選択 → セーブ選択」の場合、以下で扱いを分ける。

1. **シナリオ名一致 + チェックサム一致**
   - 通常ロード（警告なし）。
2. **シナリオ名一致 + チェックサム不一致**
   - 互換性警告を表示し、既定はロード拒否。
   - 明示オプトイン（例: 「非互換ロードを試行」）がある場合のみロード許可。
3. **シナリオ名不一致**
   - 別シナリオセーブとして扱い、既定は対象外表示またはロード拒否。

`revision` は差分説明やサポート調査に利用し、最終判定は `checksum` を優先する。

### 5.2 チェックサム算出方式に関する未確定事項（後続タスク）

チェックサムの厳密な算出方法（正規化手順・対象フィールド・命令の取捨選択）は**後続タスク**として定義する。
v0 時点では、`scenario_ref.checksum` を比較に使うことのみを規定し、算出アルゴリズムは固定しない。

検討事項の例:

- `bg`, `ch`, `bgm`, `se` などの演出系命令は、変更されてもゲーム進行に影響しないとみなし、
  チェックサム計算対象から除外するかどうか。
- 分岐や変数更新に関与する命令のみを対象にした「進行整合性チェックサム」を採用するかどうか。
- 将来、演出差分を検知する用途向けに別系統（例: 表示整合性チェックサム）を分離するかどうか。

## 6. 保存・復元の不変条件（受け入れ基準）

以下を満たす実装のみを受け入れ可能とする。

1. **同一性**: 同一シナリオ入力 + 同一セーブデータ（`state_version` 含む）から再開したとき、次に得られる進行結果（分岐、表示、乱数結果）が一致する。
2. **位置整合**: 復元直後の `position` がシナリオ上で解決可能である。
3. **選択整合**: `choice_results` に基づく分岐再評価で、保存前と異なる分岐へ逸脱しない。
4. **乱数整合**: `rng.seed` と `rng.step` が一致する限り、以後の乱数系列が一致する。
5. **シナリオ整合**: 復元時に `scenario_ref.checksum` が一致しない場合、既定動作では再開しない。
6. **検証可能性**: 上記 1〜5 を自動テストで検証できること（最低 1 ケース以上）。

## 7. v0 データ例（全体）

```json
{
  "state_version": "0",
  "scenario_ref": {
    "name": "main_story",
    "revision": "git:1d73725",
    "checksum": "3e7d6a6b9f9fca145f0f7f8fcbeb2ccac0e8a9df68ad5e8f6f2d7552edce2a00"
  },
  "position": {
    "label": "intro",
    "index": 3
  },
  "variables": {
    "player_name": "Aoi",
    "affinity": 12,
    "met_guide": true,
    "last_seen": null
  },
  "read_history": ["intro#0", "intro#1", "intro#2"],
  "log": [
    { "seq": 0, "kind": "line", "payload": { "text": "ようこそ" } },
    { "seq": 1, "kind": "choice", "payload": { "id": "c_intro_1" } }
  ],
  "choice_results": [
    { "at": "intro#2", "choice_id": "c_intro_1", "selected_index": 0 }
  ],
  "rng": {
    "seed": "project-1-slot-2-20250101",
    "step": 14
  }
}
```
