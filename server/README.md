# server

FastAPI ベースの API サーバです。

## テスト実行手順（pytest）

`pytest` 実行前に、必ず依存関係（開発用 extras 含む）をインストールしてください。

```bash
cd server
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .[dev]
pytest -q
```

> 依存インストールを省略すると、`fastapi` などが見つからずテスト収集時に失敗します。

## OpenAPI更新手順

OpenAPI スキーマは専用コマンドで更新します。

```bash
cd server
python -m pip install -e .
kamishibai-export-openapi
```

実行すると、`shared/schema/openapi.json` に UTF-8 の pretty print 形式で出力されます。


## Shared Schema 検証

`shared/schema/` の JSON Schema と検証用データの整合性を確認します。

```bash
cd server
python -m pip install -e .[dev]
kamishibai-validate-shared-schema
```
