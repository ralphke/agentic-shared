#!/usr/bin/env python3
"""Check conventional OpenSpec artifacts; external archive gates need separate evidence."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


class OpenSpecValidationError(ValueError):
    """Raised when an OpenSpec change is incomplete or malformed."""


def normalize_heading(heading: str) -> str:
    return re.sub(r"\s+", " ", heading.lower().replace("/", " / ")).strip()


def proposal_sections(content: str) -> dict[str, list[tuple[str, str]]]:
    headings = list(re.finditer(r"^(#{2,6})[ \t]+(.+?)[ \t]*$", content, re.MULTILINE))
    sections: dict[str, list[tuple[str, str]]] = {}
    for index, heading in enumerate(headings):
        level = len(heading[1])
        end = len(content)
        for following in headings[index + 1 :]:
            if len(following[1]) <= level:
                end = following.start()
                break
        name = normalize_heading(heading[2])
        sections.setdefault(name, []).append((heading[2], content[heading.end() : end]))
    return sections


def require_unique_section(
    sections: dict[str, list[tuple[str, str]]], heading: str
) -> str:
    matches = sections.get(normalize_heading(heading), [])
    if not matches:
        raise OpenSpecValidationError(f"proposal missing required section: {heading}")
    if len(matches) != 1:
        raise OpenSpecValidationError(f"proposal has duplicate section: {heading}")
    return matches[0][1]


def resolve_heading_alias(
    sections: dict[str, list[tuple[str, str]]], current: str, legacy: str
) -> str:
    current_matches = sections.get(normalize_heading(current), [])
    legacy_matches = sections.get(normalize_heading(legacy), [])
    if current_matches and legacy_matches:
        raise OpenSpecValidationError(
            f"proposal mixes conflicting sections: {current} and {legacy}"
        )
    if len(current_matches) > 1 or len(legacy_matches) > 1:
        raise OpenSpecValidationError(
            f"proposal has duplicate section for {current}/{legacy}"
        )
    if current_matches:
        return current_matches[0][1]
    if legacy_matches:
        return legacy_matches[0][1]
    raise OpenSpecValidationError(
        f"proposal missing required core section: {current} (legacy alias: {legacy})"
    )


def parse_capabilities(capability_section: str, *, legacy: bool) -> set[str]:
    capabilities: list[str] = []
    for line in capability_section.splitlines():
        bullet = re.match(r"^\s*[-*+]\s+`([^`]+)`(?:\s*:.*)?\s*$", line)
        if not bullet:
            if re.match(r"^\s*[-*+]\s+\S", line):
                raise OpenSpecValidationError(
                    "proposal capability entries must use a backticked path"
                )
            continue
        capabilities.append(bullet[1].strip())

    nonempty_lines = [
        line.strip()
        for line in capability_section.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not capabilities and any(
        line.lower() != "none." for line in nonempty_lines
    ):
        kind = "Affected Domains" if legacy else "Capabilities"
        raise OpenSpecValidationError(
            f"proposal {kind} section contains no valid capability paths"
        )

    invalid = [
        capability
        for capability in capabilities
        if (
            capability.startswith("/")
            or capability.endswith("/")
            or "\\" in capability
            or any(
                not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", segment)
                for segment in capability.split("/")
            )
        )
    ]
    if invalid:
        raise OpenSpecValidationError(
            f"proposal contains invalid capability path(s): {', '.join(invalid)}"
        )

    duplicates = sorted(
        capability for capability in set(capabilities) if capabilities.count(capability) > 1
    )
    if duplicates:
        raise OpenSpecValidationError(
            f"proposal declares duplicate capability path(s): {', '.join(duplicates)}"
        )
    return set(capabilities)


def validate_ux_applicability(ux_section: str) -> None:
    fences = re.findall(
        r"```json[ \t]*\n(.*?)\n```", ux_section, flags=re.DOTALL
    )
    if len(fences) != 1:
        raise OpenSpecValidationError(
            "proposal UX Applicability must contain exactly one JSON fence"
        )
    try:
        decision = json.loads(fences[0])
    except json.JSONDecodeError as error:
        raise OpenSpecValidationError(
            f"proposal UX Applicability is invalid JSON: {error.msg}"
        ) from error
    if not isinstance(decision, dict):
        raise OpenSpecValidationError(
            "proposal UX Applicability must be a JSON object"
        )
    if not isinstance(decision.get("required"), bool):
        raise OpenSpecValidationError(
            "proposal UX Applicability required value must be boolean"
        )
    if not isinstance(decision.get("reason"), str) or not decision["reason"].strip():
        raise OpenSpecValidationError(
            "proposal UX Applicability reason must be nonempty"
        )


def validate_proposal(proposal: str, delta_specs: list[Path], specs_root: Path) -> None:
    sections = proposal_sections(proposal)
    resolve_heading_alias(sections, "Why", "Intent")
    require_unique_section(sections, "What Changes")
    require_unique_section(sections, "Impact")
    capability_section = resolve_heading_alias(
        sections, "Capabilities", "Affected Domains"
    )
    legacy_capabilities = bool(
        sections.get(normalize_heading("Affected Domains"))
    )

    required_extensions = (
        "Scope",
        "Out of Scope",
        "Scenarios",
        "Acceptance Criteria",
        "UX Applicability",
        "Build / Buy / Vibe",
        "Legal / IP Notes",
    )
    extension_sections = {
        heading: require_unique_section(sections, heading)
        for heading in required_extensions
    }

    scenarios = extension_sections["Scenarios"]
    scenario_headings = re.findall(
        r"^#{3,6}[ \t]+Scenario:[ \t]+\S", scenarios, flags=re.MULTILINE
    )
    if len(scenario_headings) < 3:
        raise OpenSpecValidationError(
            "proposal Scenarios must contain at least three Scenario headings"
        )
    if not re.search(
        r"unhappy|error|fail|reject|denied|invalid|boundary|edge case",
        scenarios,
        flags=re.IGNORECASE,
    ):
        raise OpenSpecValidationError(
            "proposal Scenarios must include an unhappy or boundary path"
        )

    acceptance_criteria = re.findall(
        r"^\s*[-*+]\s+\[[ xX]\][ \t]+\S",
        extension_sections["Acceptance Criteria"],
        flags=re.MULTILINE,
    )
    if len(acceptance_criteria) < 3:
        raise OpenSpecValidationError(
            "proposal Acceptance Criteria must contain at least three binary items"
        )

    validate_ux_applicability(extension_sections["UX Applicability"])
    declared = parse_capabilities(capability_section, legacy=legacy_capabilities)
    actual = {
        spec.parent.relative_to(specs_root).as_posix()
        for spec in delta_specs
    }
    missing = sorted(declared - actual)
    undeclared = sorted(actual - declared)
    if missing or undeclared:
        details = []
        if missing:
            details.append(f"missing delta path(s): {', '.join(missing)}")
        if undeclared:
            details.append(f"undeclared delta path(s): {', '.join(undeclared)}")
        raise OpenSpecValidationError(
            "proposal capability mapping mismatch: " + "; ".join(details)
        )


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

    validate_proposal(artifacts["proposal.md"], delta_specs, specs_root)

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
