# Try Exciting Web Kamishibai

HTML + ES Modules だけで動く、最小構成の紙芝居ノベルエンジンです。
この README は、以下 3 つの読者を想定して構成しています。

1. **エンドユーザー（遊ぶ人）**
2. **エンジン使用者（ゲーム開発者・シナリオ作者）**
3. **エンジン開発者 / AI エージェント（機能追加・保守担当）**

---

## 1) エンドユーザー向け（遊ぶ人）

### これは何？
- ブラウザで動く短編ノベル体験です。
- クリックでテキストが進み、選択肢で分岐します。

### 遊び方
1. ローカルサーバーを起動します（`file://` 直開きは不可）。
2. ブラウザで `index.html` を開きます。
3. 画面をクリックして進行、選択肢が出たら任意の項目を選びます。

```bash
cd static
python -m http.server 8000
# ブラウザで http://127.0.0.1:8000/index.html を開く
```

### 期待される挙動
- 背景・立ち絵・話者名・本文が順次更新される。
- 選択肢によって展開が変わる。

---

## 2) エンジン使用者向け（ゲーム開発者・シナリオ作者）

### 目的
- `scenario`（台本データ）を書くだけで、分岐付きノベルを実装できるようにする。
- 描画ロジックや進行制御の詳細を意識せず、命令データ中心で制作する。

### ディレクトリ構成

```text
.
├── README.md
├── LICENSE
└── static/
    ├── index.html              # renderer + 初期化
    └── js/
        ├── engine/runtime.js   # 進行制御
        └── scenarios/sample.js # 台本データ
```

### コマンド仕様（シナリオ DSL）
`scenario` はコマンドオブジェクトの配列で構成します。

- `label: string`
  ジャンプ先ラベルを定義（表示はしない）。
- `name: string` / `text: string`
  発話者名と本文を表示。
- `bg: string` / `bgColor: string`
  背景画像 URL または CSS 背景指定を更新。
- `leftOn: boolean` / `rightOn: boolean`
  左右キャラクター表示の ON/OFF 切替。
- `left: string` / `right: string`
  左右キャラクター画像 URL を設定。
- `set: Record<string, any>`
  フラグ（状態）を更新。
- `jump: string`
  指定 `label` へジャンプ。
- `jumpIf: { key: string; equals: any; to: string }`
  条件成立時に `to` の `label` へジャンプ。
- `choice: Array<{ text: string; set?: object; jump?: string }>`
  選択肢を表示し、選択時に状態更新・ジャンプを行う。

### 最小シナリオ例

```js
{ label: "start" },
{ name: "案内役", text: "こんにちは。どちらに進みますか？" },
{ choice: [
    { text: "話しかける", set: { flag_talk: true }, jump: "talk" },
    { text: "無視する", set: { flag_talk: false }, jump: "ignore" },
  ]
},

{ label: "talk" },
{ name: "主人公", text: "話しかけてみよう。" },
{ jumpIf: { key: "flag_talk", equals: true, to: "end" } },

{ label: "ignore" },
{ set: { flag_talk: false } },
{ name: "主人公", text: "今回は見送ろう。" },
{ jump: "end" },

{ label: "end" },
{ name: "案内役", text: "おしまい。" }
```

### 制作のコツ
- 分岐の終点は `end` などの共通ラベルに寄せると保守しやすい。
- フラグ名は `flag_***` 形式で統一すると読みやすい。
- 演出（見た目）を増やしたくなったら、まず既存コマンドで代替できるか確認する。

---

## 3) エンジン開発者 / AI エージェント向け（機能追加・保守）

### アーキテクチャ原則
責務分離を崩さないこと。

- `runtime`（進行制御）
  実行順、状態遷移、分岐、ジャンプ、停止条件を扱う。
- `renderer`（描画）
  実行結果を DOM に反映（背景・立ち絵・テキスト・選択肢 UI）。
- `scenario`（データ）
  命令データのみを保持し、描画や進行ロジックを直接書かない。

> 原則: 「進行制御」「描画」「データ」を混ぜない。将来的な分割後も境界を維持する。

### 新規コマンド追加チェックリスト
- [ ] コマンドスキーマを定義し、この README の仕様を更新。
- [ ] `runtime` に実行ルールを実装（状態更新・分岐・停止条件）。
- [ ] 必要時のみ `renderer` に描画反映を追加。
- [ ] 最小利用例を README または `sample.js` に追記。
- [ ] 既存シナリオとの互換性を確認。

### AI エージェント向け運用メモ
- 既存動作を壊さない最小差分で変更する。
- 仕様変更時は README を先に/同時に更新し、意図を明文化する。
- 可能な限り「コマンド仕様」と「実装差分」を 1:1 で対応させる。
