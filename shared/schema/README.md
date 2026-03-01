# shared/schema

`shared/schema/` は **SPA が参照する API 契約（OpenAPI）** の共有配置場所です。

## 管理方針

- `openapi.json` を API 契約の正として管理する。
- セーブデータ/シナリオデータの内部スキーマは API サーバ責務とし、`server/schema/` で管理する。

## 収録ファイル

- `openapi.json`: `app.main:app` からエクスポートした OpenAPI スキーマ。
