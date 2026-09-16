#!/usr/bin/env python3
"""Contract tests for shared OpenSpec command skills."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = {
    "openspec-propose": {
        "planning only",
        "Do not edit project code",
        "openspec status --change",
    },
    "openspec-apply-change": {
        "openspec instructions apply --change",
        "contextFiles",
        "Do not mark partial or deferred work complete",
    },
    "openspec-verify-change": {
        "Completeness",
        "Correctness",
        "Coherence",
        "legal approval",
        "openspec store list --json",
        "--store <id>",
    },
    "software-fabric-kickoff": {
        "Stop after planning",
        "new explicit request",
        "Do not implement code during kickoff",
        "openspec store list --json",
        "--store <id>",
    },
}


class OpenSpecCommandSkillTests(unittest.TestCase):
    def test_command_skills_have_required_metadata_and_guards(self) -> None:
        for name, expectations in SKILLS.items():
            with self.subTest(name=name):
                path = ROOT / ".github" / "skills" / name / "SKILL.md"
                content = path.read_text(encoding="utf-8")

                self.assertTrue(content.startswith("---\n"))
                self.assertIn(f"name: {name}\n", content)
                self.assertIn("description:", content)
                self.assertIn("Node.js 26 or later", content)
                self.assertIn("openspec context --json", content)
                self.assertRegex(
                    content,
                    re.compile(r"(?:do not|never).*fall back to (?:a )?legacy prompt", re.I),
                )
                for expectation in expectations:
                    self.assertIn(expectation.lower(), content.lower())

    def test_legacy_prompts_declare_replacement_skills(self) -> None:
        mappings = {
            "opsx-propose.prompt.md": "openspec-propose",
            "opsx-apply.prompt.md": "openspec-apply-change",
            "opsx-verify.prompt.md": "openspec-verify-change",
            "sdlc-kickoff.prompt.md": "software-fabric-kickoff",
        }

        for prompt, replacement in mappings.items():
            with self.subTest(prompt=prompt):
                content = (ROOT / ".github" / "prompts" / prompt).read_text(
                    encoding="utf-8"
                )
                self.assertIn("> **Deprecated:**", content)
                self.assertIn(f"`{replacement}` skill", content)

    def test_idea_issue_and_direct_proposal_are_supported_entry_paths(self) -> None:
        proposal_skill = (
            ROOT / ".github" / "skills" / "openspec-propose" / "SKILL.md"
        ).read_text(encoding="utf-8")
        orchestrator = (ROOT / ".github" / "workflows" / "sdlc-orchestrator.yml").read_text(
            encoding="utf-8"
        )
        idea_template = (ROOT / ".github" / "ISSUE_TEMPLATE" / "idea-capture.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("GitHub issue labelled `idea`", proposal_skill)
        self.assertIn("Direct `/opsx:propose <description>` invocation is a valid alternative", proposal_skill)
        self.assertIn("labels:\n  - idea\n  - stage:proposal", idea_template)
        self.assertIn("include issue #${context.issue.number}", orchestrator)
        self.assertIn("software-fabric-kickoff skill", orchestrator)

    def test_orchestrator_uses_command_skills_for_stage_handoffs(self) -> None:
        orchestrator = (ROOT / ".github" / "workflows" / "sdlc-orchestrator.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("openspec-apply-change skill", orchestrator)
        self.assertIn("openspec-verify-change skill", orchestrator)
        self.assertNotIn("/opsx:apply", orchestrator)
        self.assertNotIn("/opsx:verify", orchestrator)


if __name__ == "__main__":
    unittest.main()