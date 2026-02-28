"""Temporary scenario linter for v0 files.

This is intentionally lightweight for early scenario authoring.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def lint_scenario(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"JSON parse error: {exc}"]

    if "id" not in data:
        errors.append("missing required field: id")
    if "nodes" not in data or not isinstance(data["nodes"], list):
        errors.append("missing required field: nodes (array)")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint scenario JSON for v0")
    parser.add_argument("file", type=Path, help="Path to scenario json")
    args = parser.parse_args()

    errors = lint_scenario(args.file)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("OK: no lint errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
