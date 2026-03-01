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

## AIエージェント向けルール（重要）

このリポジトリでAIエージェントがPRを作る場合は、`docs/AGENT_RULES.md` を必ず確認してください。
特に以下は必須です。

- PRは1つの意図だけを含める（Single Responsibility）。
- PRタイトルは `<type>: <short description>` 形式にする。
- typeは `feat|fix|refactor|test|infra|docs|chore` のみを使う。

詳細ルールは `docs/AGENT_RULES.md` を正とします。

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
npm run gen:types
npm run type-check
npm run dev -- --host 0.0.0.0 --port 5173
```

`web/src/types/` は API 生成型を配置するディレクトリです。`npm run gen:types` で `schema.d.ts`（OpenAPI）と API クライアント（`web/src/api/generated/`）を再生成してください。

生成物（`web/src/types/schema.d.ts`, `web/src/api/generated/`）は **コミット管理** します。OpenAPI 変更時は `npm run gen:types` を実行し、差分を同時に含めてください（`.gitignore` には追加しません）。

## エンジン開発者向け（CI 手順）

ローカルで CI 相当のテスト・ビルドを行う最小手順です。

API/モデル変更時は、リポジトリルートで必ず `./sync-and-check.sh` を実行してください。

- `./sync-and-check.sh` : ローカル最終確認（pytest + OpenAPI/スキーマ検証 + SPA型/クライアント生成 + type-check + 生成物差分確認）
- `./sync-and-check.sh --mode=contract` : 契約同期の軽量確認（OpenAPI/スキーマ検証 + SPA型/クライアント生成 + 生成物差分確認）

```bash
# API テスト
cd server
pip install -e .[dev]
pytest

# Web ビルド
cd ../web
npm install
npm run gen:types
npm run type-check
npm run build
```

想定 CI ジョブ:

1. Python セットアップ + `pip install -e .[dev]`
2. `pytest`
3. Node セットアップ + `npm ci`
4. `npm run gen:types`
5. `npm run type-check`
6. `npm run build`
7. `./sync-and-check.sh`（型同期を含む統合チェック）
