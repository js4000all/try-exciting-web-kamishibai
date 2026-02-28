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
