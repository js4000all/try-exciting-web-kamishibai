# API設計 v0（固定版）

本ドキュメントは、Kamishibai Engine v0 の API 契約を固定し、実装の優先順と将来拡張の境界を明確化するための基準である。

## 1. 想定ユーザーとユースケース

### 1.1 エンドユーザー（プレイヤー）

- ランチャー/ブラウザから作品一覧を開く。
- 遊ぶ作品を選択し、メタ情報（タイトル・説明・サムネイル）を確認する。
- ゲーム開始時に必要シナリオを取得し、画面を進行する。
- 参照中の背景/立ち絵/音声アセットを再生する。
- 任意スロットへセーブし、次回ロードで再開する。

### 1.2 シナリオ開発者

- プロジェクト一覧から作業対象を確認する。
- 章単位またはファイル単位でシナリオを読み込み、差分確認を行う。
- missing asset / validation error を API レスポンスから検知し、修正する。
- セーブ形式互換を保ちながら動作確認（デバッグセーブ）を行う。

---

## 2. API v0 基本方針

- バージョンプレフィックスは `/api/v0` で固定する。
- v0 は「単一サーバ内で完結する最小構成」を優先し、複雑な権限管理・非同期ジョブ・外部ストレージ依存を持ち込まない。
- レスポンスは JSON を基本とし、アセットのみバイナリ配信を許可する。
- エラー形式は共通 envelope を利用し、Web 側でそのまま表示可能な構造に統一する。

---

## 3. エンドポイント再整理（v0固定）

## 3.1 プロジェクト取得

### `GET /api/v0/projects`

用途:
- ランチャーの作品一覧表示
- 開発者の対象プロジェクト確認

レスポンス（200）:
```json
{
  "items": [
    {
      "id": "project-1",
      "title": "Sample Project",
      "summary": "v0 sample",
      "entry_chapter": "prologue",
      "updated_at": "2026-02-01T09:30:00Z"
    }
  ]
}
```

### `GET /api/v0/projects/{project_id}`

用途:
- 作品詳細表示
- プレイ開始前のメタ情報取得

レスポンス（200）:
```json
{
  "id": "project-1",
  "title": "Sample Project",
  "summary": "v0 sample",
  "entry_chapter": "prologue",
  "chapters": ["prologue", "chapter-1"],
  "scenario_revision": "2026.02.01",
  "assets_base_url": "/api/v0/assets/project-1/"
}
```

## 3.2 シナリオ取得

v0 は「章単位」と「ファイル単位」を明示的に分けて提供する。

### `GET /api/v0/projects/{project_id}/scenario/chapters/{chapter_id}`

用途:
- 再生クライアントの通常進行（章ロード）

レスポンス（200）:
```json
{
  "project_id": "project-1",
  "chapter_id": "prologue",
  "scenario": {
    "version": "v0",
    "start": "n001",
    "nodes": []
  },
  "warnings": []
}
```

### `GET /api/v0/projects/{project_id}/scenario/files/{file_path}`

用途:
- シナリオ開発者の検証/差分確認
- 将来の分割シナリオ運用の先行対応

備考:
- `file_path` は URL エンコードされた相対パス（例: `chapter-1%2Fscene-03.yaml`）。
- path traversal を防ぐため、プロジェクトルート配下のみ許可する。

## 3.3 アセット配信方式（v0固定）

### 採用: **直配信（API/Static からの直接配信）**

### `GET /api/v0/assets/{project_id}/{asset_path}`

採用理由:
1. v0 の目的は「まず確実に動くこと」であり、署名 URL の発行・期限管理・ストレージ連携はオーバーヘッドが大きい。
2. ローカル開発と CI で同一経路を使えるため、検証が単純になる。
3. 将来 CDN/オブジェクトストレージへ移行する際も、`assets_base_url` の差し替えで吸収しやすい。

運用ルール:
- Cache-Control は v0 で `public, max-age=60` を初期値とする。
- `asset_path` は `shared/specs/asset-reference.md` の規約に従う。

## 3.4 セーブ保存先（v0固定）

### 採用: **サーバ保存（プロジェクト別・スロット別）**

### `PUT /api/v0/projects/{project_id}/saves/{slot}`

用途:
- エンドユーザーの継続プレイ
- デバイス跨ぎを見据えた最低限の互換基盤

リクエスト:
- Body は `shared/specs/save-data-v0.md` に準拠。

レスポンス（200）:
```json
{
  "project_id": "project-1",
  "slot": "1",
  "saved_at": "2026-02-01T09:35:00Z"
}
```

補助取得:
- `GET /api/v0/projects/{project_id}/saves/{slot}` を v0 に含める（保存確認・ロード用）。

将来切替余地:
- v1 以降でローカル保存（IndexedDB/LocalStorage）を併用する場合は、クライアント保存アダプタ層を追加して切替可能にする。
- API 契約としては save payload を共通に保ち、保存先だけを差し替える。

---

## 4. 統一エラー形式（Web表示対応）

v0 の全 API は、4xx/5xx で以下形式を返す。

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Project not found",
    "detail": {
      "project_id": "project-x"
    },
    "request_id": "req-01HXYZ..."
  }
}
```

フィールド定義:
- `code`: 機械判定用の固定値
- `message`: そのまま画面表示可能な短文
- `detail`: 任意の補足情報（フォーム項目や対象ID）
- `request_id`: サーバログ突合用

代表コード:
- `RESOURCE_NOT_FOUND`（404）
- `VALIDATION_ERROR`（422）
- `CONFLICT`（409、セーブ世代不整合など）
- `INTERNAL_ERROR`（500）

`VALIDATION_ERROR` 例:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid save payload",
    "detail": {
      "fields": [
        {"path": "state.current_node", "reason": "required"}
      ]
    },
    "request_id": "req-01HXYZ..."
  }
}
```

---

## 5. 実装計画（v0）

### Phase 1: 契約固定（ドキュメント・型）

1. `shared/` に API レスポンス用 JSON Schema（project list/detail, error envelope）を追加する。
2. `docs/ARCHITECTURE.md` の API 節を本仕様参照に更新する。
3. OpenAPI（FastAPI 自動生成）との差分チェック手順を `server/README.md` に追加する。

### Phase 2: サーバ実装

1. ルーターを `projects`, `scenario`, `assets`, `saves` に分割。
2. `/api/v0` 配下に上記エンドポイントを実装。
3. 共通例外ハンドラでエラー envelope を強制。
4. セーブ入出力を `save-data-v0.md` に沿ってバリデーション。

### Phase 3: Web 接続

1. クライアント API 層に v0 エンドポイントを実装。
2. エラー `code` に応じた UI 表示（not found / validation）を追加。
3. セーブ/ロードの疎通確認を E2E で自動化。

### Phase 4: 受け入れ確認

- プロジェクト一覧→詳細→章ロード→アセット表示→セーブ→ロードの一連動作が通る。
- missing asset 時に warning とフォールバック表示が行える。
- 404 / 422 が統一形式で返り、Web で表示できる。

