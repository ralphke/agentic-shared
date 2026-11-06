#!/usr/bin/env python3
"""Check conventional OpenSpec artifacts; external archive gates need separate evidence."""

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

    artifacts = {
        name: (change_root / name).read_text(encoding="utf-8")
        for name in required_files
    }
    empty = [name for name, content in artifacts.items() if not content.strip()]
    if empty:
        raise OpenSpecValidationError(f"empty required file(s): {', '.join(empty)}")

    checkboxes: list[tuple[str, str]] = []
    fence: str | None = None
    fence_list_indent: int | None = None
    last_task_indent: int | None = None
    for line in artifacts["tasks.md"].splitlines():
        indent = len(line) - len(line.lstrip(" "))
        list_marker = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", line)

        if fence is not None:
            if (
                fence_list_indent is not None
                and line.strip()
                and list_marker
                and indent <= fence_list_indent
            ):
                fence = None
                fence_list_indent = None
            else:
                marker = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
                if marker and (
                    marker[1][0] == fence[0]
                    and len(marker[1]) >= len(fence)
                    and not marker[2].strip()
                ):
                    fence = None
                    fence_list_indent = None
                    continue
                else:
                    continue

        marker = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if marker:
            fence = marker[1]
            if last_task_indent is not None and indent > last_task_indent:
                fence_list_indent = last_task_indent
            else:
                fence_list_indent = None
            continue

        task = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+\[([^\]]*)\]\s*(.*)$", line)
        if task:
            checkboxes.append((task[1].strip(), task[2].strip()))
            last_task_indent = indent
    if not checkboxes or not any(description for _, description in checkboxes):
        raise OpenSpecValidationError("no usable tracked tasks found in tasks.md")
    incomplete = [
        (marker, description)
        for marker, description in checkboxes
        if marker.lower() != "x" or not description
    ]
    if incomplete:
        raise OpenSpecValidationError(
            f"{len(incomplete)} incomplete or undescribed task(s) remain in {change_root / 'tasks.md'}"
        )

    specs_root = change_root / "specs"
    delta_specs = sorted(
        spec for spec in specs_root.rglob("spec.md") if spec.parent != specs_root
    )
    if not delta_specs:
        raise OpenSpecValidationError("no delta specs found under specs/**/spec.md")

    for spec_path in delta_specs:
        content = spec_path.read_text(encoding="utf-8")
        if not content.strip():
            raise OpenSpecValidationError(f"empty delta spec: {spec_path}")
        if not re.search(
            r"^## (?:ADDED|MODIFIED|REMOVED|RENAMED) Requirements\s*$",
            content,
            flags=re.MULTILINE,
        ):
            raise OpenSpecValidationError(f"delta spec has no requirement section: {spec_path}")
        has_requirement = re.search(r"^### Requirement:[ \t]+\S", content, flags=re.MULTILINE)
        has_rename = (
            "## RENAMED Requirements" in content
            and re.search(
                r"^-\s+FROM:[ \t]+`?### Requirement:[ \t]+\S", content, re.MULTILINE
            )
            and re.search(
                r"^-\s+TO:[ \t]+`?### Requirement:[ \t]+\S", content, re.MULTILINE
            )
        )
        if not has_requirement and not has_rename:
            raise OpenSpecValidationError(f"delta spec has no requirement: {spec_path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("change_slug")
    parser.add_argument(
        "--root", type=Path, default=Path("openspec/changes")
    )
    args = parser.parse_args()

    change_root = args.root / args.change_slug
    try:
        validate_change(change_root)
    except (OSError, UnicodeError) as error:
        print(f"OpenSpec artifact read failed: {error}", file=sys.stderr)
        return 1
    except OpenSpecValidationError as error:
        print(f"OpenSpec archive readiness failed: {error}", file=sys.stderr)
        return 1

    print(
        f"OpenSpec artifact checks passed: {change_root}. "
        "External quality gates, acceptance, and spec sync remain separately required."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
