"""Validate shared JSON Schemas and fixture data for server/web type synchronization."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "shared" / "schema"

TARGETS = [
    (
        "scenario-v0.schema.json",
        "examples/scenario.valid.json",
    ),
    (
        "save-data-v0.schema.json",
        "examples/save-data.valid.json",
    ),
]


def _load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    for schema_name, fixture_name in TARGETS:
        schema_path = SCHEMA_DIR / schema_name
        fixture_path = SCHEMA_DIR / fixture_name

        schema = _load_json(schema_path)
        fixture = _load_json(fixture_path)

        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(fixture)

        print(f"Validated {fixture_path.relative_to(REPO_ROOT)} against {schema_path.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
