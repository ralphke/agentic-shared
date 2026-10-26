#!/usr/bin/env python3
"""Restore bounded Software Fabric policy blocks after OpenSpec regeneration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[2]
START = "<!-- agentic-shared:policy:start -->"
END = "<!-- agentic-shared:policy:end -->"
COMMON_POLICY = """## Software Fabric prerequisites and boundaries

Node.js 26 or later and the OpenSpec CLI are required. Before proceeding, run
`node --version` and `openspec --version`. If either is unavailable or Node.js is
older than 26, stop without changing artifacts and report the exact error and
setup requirement. Do not fall back to a legacy prompt workflow.

After store selection, run `openspec context --json` with the selected store flag,
if any. Require a resolved root before artifact work. For an uninitialized project,
follow the Project check below, including its auto-selected versus explicit-request
distinction. For any other context error, stop, report the error and suggested fix,
and make no artifact changes. Never initialize implicitly or use a stale root.
"""
SKILL_POLICIES = {
    "openspec-propose": COMMON_POLICY + """
The primary non-developer intake is a GitHub issue labelled `idea`. Use its title,
fields, labels, and discussion as proposal input; retain `idea` and `stage:proposal`
until approval. Direct `/opsx:propose <description>` invocation is a valid alternative
and does not require an issue. This workflow authorizes planning only:
Do not edit project code. Stop after planning and wait for a new explicit request
before implementation.""",
    "openspec-apply-change": COMMON_POLICY + """
Do not mark partial or deferred work complete. Complete each task's specified
behavior and verification before checking it off. Preserve the testing, security,
required legal review, code review, and archive gates; task completion does not
authorize merge, deployment, or archive.""",
    "openspec-verify-change": COMMON_POLICY + """
Verification is advisory and does not grant security clearance or legal approval.
Report unmet or unverifiable mandatory gates separately from schema applicability:
passing tests, at least 80% new-code coverage, no HIGH or CRITICAL security findings,
required legal approval for legal-risk changes, code-review approval, and green CI.
Do not declare archive readiness while any applicable mandatory gate is unmet or
unverifiable. Do not implement or archive during verification.""",
}


@dataclass(frozen=True)
class Target:
    path: Path
    intro: str
    policy: str
    skill_name: str | None = None

    def block(self, newline: bytes) -> bytes:
        return f"{START}\n{self.policy}\n{END}\n\n".encode("utf-8").replace(b"\n", newline)


INTRODUCTIONS = {
    "openspec-propose": "Propose a new change - create the change and generate all artifacts in one step.",
    "openspec-apply-change": "Implement tasks from an OpenSpec change.",
    "openspec-verify-change": "Verify that an implementation matches the change artifacts (specs, tasks, design).",
}
PROMPTS = {
    "opsx-propose": "openspec-propose",
    "opsx-apply": "openspec-apply-change",
    "opsx-verify": "openspec-verify-change",
}
TARGETS = tuple(
    Target(
        Path(".github") / "skills" / name / "SKILL.md",
        INTRODUCTIONS[name],
        policy,
        name,
    )
    for name, policy in SKILL_POLICIES.items()
) + tuple(
    Target(
        Path(".github") / "prompts" / f"{prompt}.prompt.md",
        INTRODUCTIONS[skill],
        "> **Deprecated:** This wrapper is retained for one compatibility release. Use the\n"
        f"> `{skill}` skill for new workflows. Use this legacy wrapper only when\n"
        "> the user explicitly invokes its literal `/opsx:` command.",
    )
    for prompt, skill in PROMPTS.items()
)


class RestorationError(ValueError):
    """An unsupported target must be reconciled deliberately, not guessed."""


def restored_content(target: Target, original: bytes) -> bytes:
    def invalid(reason: str) -> RestorationError:
        return RestorationError(f"{target.path}: {reason}; review the generated diff before retrying")

    try:
        text = original.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise invalid("expected UTF-8 content") from exc
    header = re.match(rb"\A---(\r?\n)(.*?)\1---\1\1", original, re.DOTALL)
    if header is None:
        raise invalid("expected YAML frontmatter followed by one blank line")
    try:
        metadata = yaml.safe_load(header[2].decode("utf-8"))
    except yaml.YAMLError as exc:
        raise invalid(f"invalid YAML frontmatter: {exc}") from exc
    if not isinstance(metadata, dict) or not isinstance(metadata.get("description"), str):
        raise invalid("frontmatter must contain a string description")
    if not metadata["description"].strip():
        raise invalid("frontmatter description is empty")
    if target.skill_name and metadata.get("name") != target.skill_name:
        raise invalid(f"frontmatter name must be {target.skill_name}")
    if text.splitlines().count(target.intro) != 1:
        raise invalid("expected exactly one generated introduction anchor")

    newline = header[1]
    block = target.block(newline)
    body = original[header.end():]
    if "agentic-shared:policy" in text:
        if text.count("agentic-shared:policy") != 2 or not body.startswith(block):
            raise invalid("malformed, misplaced, duplicate, or conflicting policy block")
        body = body[len(block):]
        if not body.startswith(target.intro.encode("utf-8") + newline + newline):
            raise invalid("policy block must precede the generated introduction")
        return original
    if not body.startswith(target.intro.encode("utf-8") + newline + newline):
        raise invalid("unsupported layout before the generated introduction")
    return original[:header.end()] + block + body


def restore(root: Path) -> list[str]:
    root = root.resolve()
    planned: list[tuple[Path, bytes, bytes]] = []
    for target in TARGETS:
        path = root / target.path
        if path.resolve() != path or any(parent.is_symlink() for parent in (path, *path.parents)):
            raise RestorationError(f"{target.path}: symlink or redirected target is not supported")
        try:
            original = path.read_bytes()
        except OSError as exc:
            raise RestorationError(f"{target.path}: cannot read target: {exc}") from exc
        planned.append((path, original, restored_content(target, original)))

    messages: list[str] = []
    changed: list[str] = []
    for path, original, updated in planned:
        relative = str(path.relative_to(root))
        try:
            if path.read_bytes() != original:
                raise RestorationError(f"{relative}: changed since preflight")
            if updated != original:
                path.write_bytes(updated)
                changed.append(relative)
                messages.append(f"Restored: {relative}")
            else:
                messages.append(f"Already correct: {relative}")
        except (OSError, RestorationError) as exc:
            completed = ", ".join(changed) or "none"
            raise RestorationError(
                f"{relative}: write phase failed: {exc}; completed writes: {completed}. "
                "The failing file may be partially written; inspect it before retrying."
            ) from exc
    return messages


def main() -> int:
    try:
        messages = restore(ROOT)
    except RestorationError as exc:
        print(f"Restoration failed: {exc}", file=sys.stderr)
        return 1
    for message in messages:
        print(message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
