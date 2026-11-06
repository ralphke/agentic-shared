#!/usr/bin/env python3
"""Validate conditional UX artifacts without imposing UX work on nonvisual changes."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


class UXGateError(ValueError):
    """A required declaration or artifact is invalid."""


class PendingChecks(UXGateError):
    """Configured automation has not completed yet."""


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise UXGateError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(text: str) -> object:
    return json.loads(text, object_pairs_hook=unique_object)


def outside_fences(text: str) -> list[str]:
    lines: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            if fence is None:
                fence = marker[1]
            elif marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            lines.append("")
        else:
            lines.append(line if fence is None else "")
    return lines


def artifact(change: Path, name: str) -> str:
    path = change / name
    if not path.resolve().is_relative_to(change):
        raise UXGateError(f"artifact escapes change directory: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise UXGateError(f"empty required artifact: {path}")
    return text


def applicability(change: Path) -> bool:
    text = artifact(change, "proposal.md")
    visible = outside_fences(text)
    starts = [
        i for i, line in enumerate(visible)
        if re.fullmatch(r"## UX Applicability\s*", line)
    ]
    if len(starts) != 1:
        raise UXGateError(f"{change}: require exactly one ## UX Applicability section")
    start = starts[0] + 1
    end = next(
        (i for i in range(start, len(visible)) if re.match(r"^#{1,2}\s", visible[i])),
        len(visible),
    )
    section = "\n".join(text.splitlines()[start:end]).strip()
    match = re.fullmatch(r"```json\s*\n(.*?)\n```\s*", section, re.DOTALL)
    if not match:
        raise UXGateError(f"{change}: applicability must be one fenced JSON object")
    value = parse_json(match[1])
    if (
        not isinstance(value, dict)
        or type(value.get("required")) is not bool
        or not isinstance(value.get("reason"), str)
        or not value["reason"].strip()
        or set(value) != {"required", "reason"}
    ):
        raise UXGateError(f"{change}: require boolean required and nonempty reason")
    return value["required"]


def brief_criteria(change: Path) -> set[str]:
    lines = outside_fences(artifact(change, "ux-brief.md"))
    criteria = [
        match[1] for line in lines
        if (match := re.fullmatch(r"### (UX-\d+):\s+[^<>\s].*", line))
    ]
    if not criteria or len(criteria) != len(set(criteria)):
        raise UXGateError(f"{change}: brief needs unique ### UX-01: Outcome criteria")
    return set(criteria)


def validate_report(change: Path, criteria: set[str]) -> None:
    report = parse_json(artifact(change, "ux-validation.json"))
    if not isinstance(report, dict) or not isinstance(report.get("criteria"), list):
        raise UXGateError(f"{change}: report must contain a criteria list")
    seen: set[str] = set()
    for entry in report["criteria"]:
        if not isinstance(entry, dict) or not all(
            isinstance(entry.get(key), str) and entry[key].strip()
            for key in ("id", "method", "result", "evidence")
        ):
            raise UXGateError(f"{change}: each criterion needs id, method, result, evidence")
        identifier = entry["id"]
        if identifier in seen or identifier not in criteria:
            raise UXGateError(f"{change}: duplicate or unknown criterion {identifier}")
        if entry["method"] not in ("automated", "manual") or entry["result"] != "passed":
            raise UXGateError(f"{change}: criterion {identifier} is not validated as passed")
        seen.add(identifier)
    if missing := criteria - seen:
        raise UXGateError(f"{change}: missing criterion evidence: {', '.join(sorted(missing))}")


def configured_checks(text: str) -> list[str]:
    names = parse_json(text)
    if (
        not isinstance(names, list) or not names
        or not all(isinstance(name, str) and name.strip() == name and name for name in names)
        or len(names) != len(set(names))
    ):
        raise UXGateError("UX_CHECK_NAMES must be a nonempty JSON list of unique check names")
    if any(re.search(r"\bStage: (UX Design|Design|Test|Security)$", name) for name in names):
        raise UXGateError("UX_CHECK_NAMES must not name an orchestrator stage gate")
    return names


def evaluate_checks(runs: object, names: list[str], head: str) -> None:
    if not isinstance(runs, list) or not all(isinstance(run, dict) for run in runs):
        raise UXGateError("invalid GitHub check-run response")
    pending: list[str] = []
    for name in names:
        matching = [run for run in runs if run.get("name") == name]
        if not matching:
            pending.append(name)
            continue
        if len(matching) != 1:
            raise UXGateError(f"ambiguous UX check name: {name}")
        run = matching[0]
        if run.get("head_sha") != head:
            raise UXGateError(f"stale UX check revision: {name}")
        if run.get("status") != "completed":
            pending.append(name)
        elif run.get("conclusion") != "success":
            raise UXGateError(f"required UX check did not succeed: {name}")
    if pending:
        raise PendingChecks(f"required UX checks missing or pending: {', '.join(pending)}")


def fetch_checks(repository: str, head: str) -> list[dict[str, object]]:
    response = subprocess.run(
        ["gh", "api", "--paginate", "--slurp",
         f"repos/{repository}/commits/{head}/check-runs?filter=latest&per_page=100"],
        capture_output=True, text=True, check=True, timeout=30,
    )
    pages = parse_json(response.stdout)
    if not isinstance(pages, list) or not pages:
        raise UXGateError("invalid paginated GitHub check-run response")
    runs: list[dict[str, object]] = []
    for page in pages:
        if (
            not isinstance(page, dict) or not isinstance(page.get("check_runs"), list)
            or not all(isinstance(run, dict) for run in page["check_runs"])
        ):
            raise UXGateError("invalid GitHub check-run page")
        runs.extend(page["check_runs"])
    return runs


def wait_for_checks(repository: str, head: str, names: list[str], timeout: int = 300) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise UXGateError("a valid GitHub repository is required for visual completion")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", head):
        raise UXGateError("a full PR head SHA is required for visual completion")
    deadline = time.monotonic() + timeout
    while True:
        try:
            evaluate_checks(fetch_checks(repository, head), names, head)
            return
        except PendingChecks as error:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise UXGateError(f"timed out: {error}") from error
            print(str(error), flush=True)
            time.sleep(min(10, remaining))


def validate_change(change: Path, root: Path, phase: str) -> bool:
    root = root.resolve()
    resolved = change.resolve()
    if (
        resolved.parent != root
        or resolved.name == "archive"
        or change.is_symlink()
        or not resolved.is_dir()
    ):
        raise UXGateError(f"expected an active change directory inside {root}: {change}")
    required = applicability(resolved)
    if not required:
        print(f"{change.name}: UX not applicable; no UX artifacts or tests required. "
              "Use stage:design; functional gates remain required.")
        return False
    if phase != "ux":
        criteria = brief_criteria(resolved)
        if phase in ("complete", "security"):
            validate_report(resolved, criteria)
    print(f"{change.name}: visual UX required ({phase}).")
    return True


def changed_changes(root: Path, base: str, head: str) -> list[Path]:
    for revision in (base, head):
        if not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
            raise UXGateError("base and head must be full commit SHAs")
    result = subprocess.run(
        ["git", "diff", "--name-only", "-z", base, head],
        capture_output=True, text=True, check=True,
    )
    prefix = root.as_posix().rstrip("/") + "/"
    if root.is_absolute():
        raise UXGateError("diff discovery requires a repository-relative changes root")
    paths: set[Path] = set()
    for name in result.stdout.split("\0"):
        if name.startswith(prefix):
            slug = name[len(prefix):].split("/")[0]
            if slug and slug != "archive":
                change = root / slug
                if change.is_dir():
                    paths.add(change)
                elif not name.endswith("/"):
                    print(f"{change}: removed change excluded from active handoff.")
    if not paths:
        raise UXGateError("no active change folders found in the PR diff")
    return sorted(paths)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("changes", nargs="*", type=Path)
    parser.add_argument("--root", type=Path, default=Path("openspec/changes"))
    parser.add_argument(
        "--phase", choices=("ux", "design", "test", "complete", "security"), required=True,
    )
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    args = parser.parse_args()
    try:
        changes = args.changes
        if not changes:
            if not args.base or not args.head:
                raise UXGateError("provide change directories or both --base and --head")
            changes = changed_changes(args.root, args.base, args.head)
        visual = False
        for change in changes:
            visual = validate_change(change, args.root, args.phase) or visual
        if visual and args.phase in ("complete", "security"):
            names = configured_checks(os.environ.get("UX_CHECK_NAMES", ""))
            wait_for_checks(args.repository, args.head or "", names)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        print(f"UX gate command failed: {error}; {error.stderr or ''}", file=sys.stderr)
        return 1
    except (OSError, UnicodeError, ValueError) as error:
        print(f"UX gate failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
