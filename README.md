# 目的

このリポジトリは、HTML 1 ファイルで動く「最小の紙芝居ノベル」実装です。  
シナリオ（台本）をコマンド配列として書き、クリックで進行・条件分岐・選択肢遷移を行う構成を目指します。

# ディレクトリ構成

```text
.
├── README.md
├── LICENSE
└── static/
    ├── index.html                    # renderer + 初期化
    └── js/
        ├── engine/
        │   ├── runtime.js            # 進行制御
        │   └── validateScript.js     # 台本検証
        └── scenarios/sample.js       # 台本データ
```


# 起動方法

ES Modules を利用しているため、`file://` で直接開かずにローカルサーバー経由で起動してください。

```bash
cd static
python -m http.server 8000
# http://127.0.0.1:8000/index.html を開く
```

# コマンド仕様

`script` 配列の 1 要素が 1 コマンドです。`createRuntime` 初期化時に `validateScript` が実行され、以下の仕様違反を検出します。

## コマンドキー（必須/任意）

| コマンド | 必須キー | 任意キー | 説明 |
| --- | --- | --- | --- |
| `label` | `label: string` | - | ジャンプ先の目印を定義（表示はしない）。 |
| 発話 | - | `name: string`, `text: string` | 発話者名と本文を表示。 |
| 背景 | - | `bg: string`, `bgColor: string` | 背景画像 URL または CSS 背景指定を更新。 |
| 立ち絵 | - | `leftOn: boolean`, `rightOn: boolean`, `left: string`, `right: string` | 左右キャラクターの表示/画像を更新。 |
| フラグ更新 | - | `set: Record<string, any>` | 状態フラグを更新。 |
| `jump` | `jump: string` | - | 指定 `label` へジャンプ。 |
| `jumpIf` | `jumpIf.key`, `jumpIf.equals`, `jumpIf.to` | - | 条件成立時のみ `to` の `label` へジャンプ。 |
| `choice` | `choice: Array<Choice>` | - | 選択肢を表示。 |
| `Choice` | `text: string` | `set?: object`, `jump?: string` | 選択時に状態更新・ジャンプ。 |

## 検証でチェックされる項目

- `label` の重複（どの index と重複したかも表示）
- `jump` / `jumpIf.to` / `choice[].jump` の未定義ラベル参照
- `choice` が配列形式であること
- `choice[].text` が必須で、空でない文字列であること

## 検証エラーの読み方

検証エラーには配列 index が `[...]` 形式で付きます。例:

```text
スクリプト検証エラー:
[5] choice は配列で指定してください。
[9] jumpIf.to ラベル "ending" が未定義です。
```

- `[5]` は `script[5]` のコマンドが不正という意味です。
- 修正後に再読み込みすると、`createRuntime` が再検証して起動します。

## シナリオ作者向けサンプル（現行台本から抜粋）

```js
{ label: "start" }

{ choice: [
    { text: "話しかける", set: { flag_talk: true }, jump: "talk" },
    { text: "無視する", set: { flag_talk: false }, jump: "ignore" },
  ]
}

{ label: "talk" }
{ jumpIf: { key: "flag_talk", equals: true, to: "end" } }

{ label: "ignore" }

{ set: { flag_talk: false } }
{ jump: "end" }
```

上記で `label / jump / jumpIf / choice / set` の基本的な使い方を確認できます。

# 拡張ルール

機能追加時は、以下の責務分離を必ず守ってください。

- `runtime`（進行制御）: どのコマンドをいつ実行し、状態遷移・分岐・ジャンプをどう行うか。
- `renderer`（描画）: 実行結果を DOM にどう反映するか（背景・立ち絵・テキスト・選択肢 UI）。
- `scenario`（データ）: 台本そのもの。命令データのみを持ち、描画ロジックを直接書かない。

> 原則: 「進行制御」と「描画」と「データ」を混ぜない。将来的にファイル分割する場合もこの境界を維持すること。

## 新規コマンド追加チェックリスト

- [ ] コマンドのスキーマを定義・追記する（README の「コマンド仕様」を更新）。
- [ ] `runtime` に実行ルールを実装する（状態更新・分岐・停止条件を明確化）。
- [ ] 必要なら `renderer` の反映処理を実装する（見た目変更がある場合）。
- [ ] README に利用例（最小サンプル）を追記する。
- [ ] 既存シナリオで互換性確認を行う。
