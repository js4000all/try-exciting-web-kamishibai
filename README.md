# 目的

このリポジトリは、HTML 1 ファイルで動く「最小の紙芝居ノベル」実装です。  
シナリオ（台本）をコマンド配列として書き、クリックで進行・条件分岐・選択肢遷移を行う構成を目指します。

# ディレクトリ構成

```text
.
├── README.md
├── LICENSE
└── static/
    ├── index.html             # renderer + 初期化
    └── js/
        ├── engine/runtime.js  # 進行制御
        └── scenarios/sample.js # 台本データ
```


# 起動方法

ES Modules を利用しているため、`file://` で直接開かずにローカルサーバー経由で起動してください。

```bash
cd static
python -m http.server 8000
# http://127.0.0.1:8000/index.html を開く
```

# コマンド仕様

`static/index.html` の `script` 配列は、以下のようなコマンド（オブジェクト）で構成します。

- `label: string`  
  ジャンプ先の目印を定義します（表示はしない）。
- `name: string` / `text: string`  
  発話者名と本文を表示します。
- `bg: string` / `bgColor: string`  
  背景画像 URL または CSS 背景指定を更新します。
- `leftOn: boolean` / `rightOn: boolean`  
  左右キャラクター表示の ON/OFF を切り替えます。
- `left: string` / `right: string`  
  左右キャラクター画像 URL を設定します。
- `set: Record<string, any>`  
  フラグ（状態）を更新します。
- `jump: string`  
  指定 `label` へジャンプします。
- `jumpIf: { key: string; equals: any; to: string }`  
  条件成立時のみ `to` の `label` へジャンプします。
- `choice: Array<{ text: string; set?: object; jump?: string }>`  
  選択肢を表示し、選択時に状態更新・ジャンプを行います。

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
