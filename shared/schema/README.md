# shared/schema

`shared/schema/` は `server` と `web` の型同期における **唯一のソース・オブ・トゥルース（JSON Schema）** です。

## 管理方針

- 型同期方式は **JSON Schema 管理** を採用する（OpenAPI は API 契約のみ）。
- シナリオ/セーブデータの契約はここに配置し、`server` と `web` はこの定義に依存する。

## 収録ファイル

- `scenario-v0.schema.json`: シナリオ JSON Schema。
- `save-data-v0.schema.json`: セーブデータ JSON Schema。
- `openapi.json`: `app.main:app` からエクスポートした OpenAPI スキーマ。
- `examples/scenario.valid.json`: シナリオ正例（スキーマ検証用）。
- `examples/save-data.valid.json`: セーブデータ正例（スキーマ検証用）。
