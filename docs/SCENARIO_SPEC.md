# シナリオ仕様書（初期版）

## 目的
本仕様は、ノベル実行機が読み込むシナリオの**共通データモデル**を定義する。シナリオファイル自体の記法（YAML / JSON / DSL）はパーサ層で吸収し、実行機内部では同一の中間表現（命令列＋ラベル辞書＋変数ストア）として扱う。これにより、将来フォーマットを追加・切替してもランタイムの実装を再利用できる。

## 1. 当面のフォーマット方針
当面は**YAML**を公式フォーマットとする。理由は、ゲーム開発者が直接読み書きして評価する初期フェーズにおいて、JSONより可読性が高く、コメントも記述しやすく、また独自DSLより学習コスト・実装コスト（パーサ保守、エラーメッセージ設計）を低く抑えられるためである。加えて、データモデルを先に固定することで、将来的にJSONやDSLを追加する場合も「入力パーサ差し替え」のみで対応可能にする。

## 2. 最低命令セット
初期実装の命令は次の11個に限定する。

- `say`（台詞表示）
- `bg`（背景切替）
- `ch`（キャラ表示/更新）
- `se`（効果音再生）
- `bgm`（BGM制御）
- `wait`（待機）
- `choice`（選択肢表示）
- `jump`（ラベル遷移）
- `label`（遷移先定義）
- `set`（変数代入）
- `if`（条件分岐）

## 3. 命令仕様（必須/任意フィールド・型・実行時意味）

| 命令 | 必須フィールド | 任意フィールド | 型 | 実行時意味 |
|---|---|---|---|---|
| `say` | `text` | `speaker`, `voice`, `expr` | `text/speaker/voice/expr: string` | テキストを表示。`speaker`があれば名前欄更新。 |
| `bg` | `id` | `transition`, `duration_ms` | `id/transition: string`, `duration_ms: number` | 背景を指定IDへ切替。トランジション指定時は演出付き。 |
| `ch` | `id` | `slot`, `pose`, `expr`, `visible` | `id/slot/pose/expr: string`, `visible: boolean` | キャラクタースロット状態を更新（表示/表情/立ち位置）。 |
| `se` | `id` | `volume`, `loop` | `id: string`, `volume: number(0-1)`, `loop: boolean` | 効果音を再生。`loop=true`でループ。 |
| `bgm` | `action` | `id`, `volume`, `fade_ms` | `action: enum(start/stop/pause/resume)`, `id: string`, `volume: number(0-1)`, `fade_ms: number` | BGM開始/停止/一時停止/再開。`start`時は`id`必須。 |
| `wait` | `ms` | なし | `ms: number` | 指定ミリ秒だけ進行を停止。 |
| `choice` | `options` | `prompt` | `prompt: string`, `options: Option[]` (`Option={text:string, jump:string}`) | 選択肢を表示し、選択された`jump`先へ遷移。 |
| `jump` | `to` | なし | `to: string` | 指定ラベルへ無条件遷移。 |
| `label` | `name` | なし | `name: string` | 現在位置にラベルを定義。実行時副作用なし。 |
| `set` | `var`, `value` | `op` | `var: string`, `value: scalar`, `op: enum(assign/add/sub)` | 変数ストアを更新。既定`op=assign`。 |
| `if` | `cond`, `then` | `else` | `cond: Expr`, `then: Command[]`, `else: Command[]` | 条件評価し、真なら`then`、偽なら`else`を順次実行。 |

> `Expr`は初期版で最小限（例: `{"eq":["flag", true]}`）とし、比較・論理演算を段階的に拡張する。

## 4. `shared` 配下への最小サンプル配置計画
実装着手時に、次の1ファイルを追加する計画とする。

- 予定パス: `shared/scenarios/minimal_branch.yaml`
- 内容要件:
  - `label: start` から開始
  - `say` で導入テキスト表示
  - `choice` で2択を提示
  - 各選択肢はそれぞれ別ラベルへ `jump`
  - 各分岐先で `say` を1回以上実行
  - 共通終端ラベルへ `jump` して合流
- 検証観点:
  - すべての`jump`先ラベルが存在する
  - `choice.options` が1件以上ある
  - 実行機が無限ループせず終端まで到達できる

## 5. 初期目標
初期マイルストーンは**「上記最小サンプルが実行機で最後まで再生できること」**とする。到達基準は、開始ラベルから選択肢のいずれを選んでも終端ラベルへ到達し、実行時エラー（未定義ラベル、型不正、必須項目欠落）が発生しないこと。
