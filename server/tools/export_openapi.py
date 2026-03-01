"""Export OpenAPI schema from app.main:app to shared/schema."""

from __future__ import annotations

import json
from pathlib import Path

from app.main import app


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "shared" / "schema" / "openapi.json"


def main() -> int:
    schema = app.openapi()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Exported OpenAPI schema to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
