#!/usr/bin/env bash
set -euo pipefail

current_step="初期化"

on_error() {
  local exit_code=$?
  echo "[ERROR] '${current_step}' で失敗しました (exit code: ${exit_code})" >&2
  exit "${exit_code}"
}

trap on_error ERR

log_start() {
  local step="$1"
  echo "[START] ${step}"
}

log_done() {
  local step="$1"
  echo "[DONE] ${step}"
}

current_step="server: pytest"
log_start "${current_step}"
(
  cd server
  pytest
)
log_done "${current_step}"

current_step="server: OpenAPI export (kamishibai-export-openapi)"
log_start "${current_step}"
(
  cd server
  kamishibai-export-openapi
)
log_done "${current_step}"

current_step="web: API 型生成 (npm run gen:api-types)"
log_start "${current_step}"
(
  cd web
  npm run gen:api-types
)
log_done "${current_step}"

current_step="web: TypeScript 型チェック (npm run type-check)"
log_start "${current_step}"
(
  cd web
  npm run type-check
)
log_done "${current_step}"

echo "[DONE] sync-and-check.sh が正常終了しました"
