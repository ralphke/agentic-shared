#!/usr/bin/env python3
"""Validate that an OpenSpec change is ready for archive review."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


class OpenSpecValidationError(ValueError):
    """Raised when an OpenSpec change is incomplete or malformed."""


def validate_change(change_root: Path) -> None:
    required_files = ("proposal.md", "design.md", "tasks.md")
    missing = [name for name in required_files if not (change_root / name).is_file()]
    if missing:
        raise OpenSpecValidationError(f"missing required file(s): {', '.join(missing)}")

    tasks = (change_root / "tasks.md").read_text(encoding="utf-8")
    unchecked = re.findall(r"^- \[ \]", tasks, flags=re.MULTILINE)
    if unchecked:
        raise OpenSpecValidationError(
            f"{len(unchecked)} unchecked task(s) remain in {change_root / 'tasks.md'}"
        )

    delta_specs = list((change_root / "specs").glob("*/spec.md")) if (change_root / "specs").is_dir() else []
    if not delta_specs:
        raise OpenSpecValidationError("no delta specs found under specs/*/spec.md")

    for spec_path in delta_specs:
        content = spec_path.read_text(encoding="utf-8")
        if "## ADDED Requirements" not in content and "## MODIFIED Requirements" not in content and "## REMOVED Requirements" not in content:
            raise OpenSpecValidationError(f"delta spec has no requirement section: {spec_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("change_slug")
    parser.add_argument(
        "--root", type=Path, default=Path("spec/openspec/changes")
    )
    args = parser.parse_args()

    change_root = args.root / args.change_slug
    try:
        validate_change(change_root)
    except FileNotFoundError as error:
        print(f"OpenSpec path not found: {error.filename}", file=sys.stderr)
        return 1
    except OpenSpecValidationError as error:
        print(f"OpenSpec archive readiness failed: {error}", file=sys.stderr)
        return 1

    print(f"OpenSpec archive readiness passed: {change_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
