# Kamishibai Engine (v0)

v0 前提のモノレポ構成です。

## リポジトリ構成

- `server/`: FastAPI ベースの API サーバ
- `web/`: Vite + React + TypeScript の描画クライアント
- `shared/`: 言語横断で共有する schema / 仕様
- `docs/`: 設計ドキュメント
- `scripts/` (任意・推奨): 将来の開発補助スクリプト置き場
- `.github/workflows/` (任意・推奨): CI 定義

> v0 では `server/`, `web/`, `shared/` を必須ディレクトリとして扱います。

## 読者ごとの requirements

### エンドユーザー

- 必須: Python 3.11+
- 到達目標: API サーバが起動し、`/health` が返ること

### シナリオ開発者

- 必須: Python 3.11+
- 到達目標: API サーバを起動し、シナリオ向け開発ツール（暫定リンター）を実行できること

### エンジン開発者

- 必須: Python 3.11+ / Node.js 20+
- 到達目標: CI 相当の API テストと Web ビルドが通ること

## 初回セットアップ（最短）

### 1) API サーバ（エンドユーザー向け）

`server/` は `pyproject.toml` を採用し、起動スクリプトを定義しています。

```bash
cd server
python -m venv .venv               # 推奨オプション
source .venv/bin/activate          # 推奨オプション
pip install -e .
kamishibai-api
```

起動確認:

```bash
curl http://localhost:8000/health
```

### 2) シナリオ開発者向け（暫定ツール）

```bash
# API サーバ起動（上記参照）
cd server
python tools/scenario_linter.py ../examples/scenario.json
```

> `examples/scenario.json` は未同梱です。v0 では lint ツールのインターフェースを先行定義しています。

### 3) Web クライアント（必要な場合）

```bash
cd web
npm install
npm run gen:api-types
npm run type-check
npm run dev -- --host 0.0.0.0 --port 5173
```

`web/src/types/` は OpenAPI 由来の型定義を配置する専用ディレクトリです。生成物は `web/src/types/schema.d.ts` に集約し、`npm run gen:api-types` で再生成してください。

型定義生成物（`web/src/types/schema.d.ts`）は **コミット管理** します。OpenAPI 変更時は `npm run gen:api-types` を実行し、差分を同時に含めてください（`.gitignore` には追加しません）。

## エンジン開発者向け（CI 手順）

ローカルで CI 相当のテスト・ビルドを行う最小手順です。

API/モデル変更時は、リポジトリルートで必ず `./sync-and-check.sh` を実行してください。

```bash
# API テスト
cd server
pip install -e .[dev]
pytest

# Web ビルド
cd ../web
npm install
npm run gen:api-types
npm run type-check
npm run build
```

想定 CI ジョブ:

1. Python セットアップ + `pip install -e .[dev]`
2. `pytest`
3. Node セットアップ + `npm ci`
4. `npm run gen:api-types`
5. `npm run type-check`
6. `npm run build`
