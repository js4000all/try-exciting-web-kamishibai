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

current_step="server: Shared schema validate (kamishibai-validate-shared-schema)"
log_start "${current_step}"
(
  cd server
  kamishibai-validate-shared-schema
)
log_done "${current_step}"

current_step="web: 型生成 (npm run gen:types)"
log_start "${current_step}"
(
  cd web
  npm run gen:types
)
log_done "${current_step}"

current_step="web: TypeScript 型チェック (npm run type-check)"
log_start "${current_step}"
(
  cd web
  npm run type-check
)
log_done "${current_step}"

current_step="generated artifacts: 差分チェック"
log_start "${current_step}"
git diff --exit-code -- shared/schema/openapi.json web/src/types/schema.d.ts web/src/types/scenario-schema.d.ts web/src/types/save-data-schema.d.ts
log_done "${current_step}"

echo "[DONE] sync-and-check.sh が正常終了しました"
