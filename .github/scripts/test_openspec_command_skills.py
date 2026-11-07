"""Contracts for independently owned OpenSpec and Fabric workflows."""

from pathlib import Path
import sys
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".github" / "skills" / "fabric-propose" / "scripts"))
from route_fabric_workflow import ACTIONS, route


class OpenSpecCommandSkillTests(unittest.TestCase):
    def test_default_and_explicit_standalone_routes_select_separate_skills(self) -> None:
        for action in ACTIONS:
            with self.subTest(action=action):
                default = route(action)
                standalone = route(action, "standalone")
                self.assertNotEqual(default["skill"], standalone["skill"])
                for result in (default, standalone):
                    path = ROOT / ".github" / "skills" / result["skill"] / "SKILL.md"
                    self.assertTrue(path.is_file(), path)
                    metadata = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
                    self.assertEqual(metadata["name"], result["skill"])
                    self.assertEqual(result["repository_controls"], "unchanged")
                    self.assertEqual(result["kind"], "advisory")
                fabric = (ROOT / ".github" / "skills" / default["skill"] / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                self.assertIn(standalone["skill"], fabric)
                self.assertIn("standalone", fabric)

    def test_unknown_modes_and_actions_are_not_silent_defaults(self) -> None:
        for action, mode in (("apply", "automatic"), ("delete", "fabric")):
            with self.subTest(action=action, mode=mode):
                with self.assertRaises(ValueError):
                    route(action, mode)

    def test_upstream_skills_do_not_embed_fabric_policy(self) -> None:
        for suffix in ACTIONS.values():
            path = ROOT / ".github" / "skills" / f"openspec-{suffix}" / "SKILL.md"
            with self.subTest(path=path):
                content = path.read_text(encoding="utf-8")
                self.assertNotIn("agentic-shared:policy", content)
                self.assertNotIn("Mandatory Fabric preflight", content)
                self.assertNotIn("Node.js 26", content)
                self.assertNotIn("fabric-workflow.instructions.md", content)
        self.assertFalse((ROOT / ".github" / "scripts" / "restore_openspec_contracts.py").exists())
        self.assertEqual(list((ROOT / ".github" / "prompts").glob("*.prompt.md")), [])

    def test_fabric_apply_blocks_missing_acceptance_before_implementation(self) -> None:
        content = (
            ROOT / ".github" / "skills" / "fabric-apply-change" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Missing or stale acceptance evidence blocks implementation", content)
        self.assertIn("Report the blocker and stop before code edits", content)
        self.assertLess(content.index("Missing or stale acceptance"), content.index("**Implement tasks"))
        upstream = (
            ROOT / ".github" / "skills" / "openspec-apply-change" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("Mandatory Planning Contract", upstream)

    def test_orchestrator_and_intake_use_fabric_owned_entry_points(self) -> None:
        orchestrator = (ROOT / ".github" / "workflows" / "sdlc-orchestrator.yml").read_text(
            encoding="utf-8"
        )
        for name in ("fabric-apply-change", "fabric-verify-change"):
            self.assertIn(f"{name} skill", orchestrator)
        self.assertIn("software-fabric-kickoff skill", orchestrator)
        proposal = (ROOT / ".github" / "skills" / "fabric-propose" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("GitHub issue labelled `idea`", proposal)
        self.assertIn("/fabric-propose <description>", proposal)


if __name__ == "__main__":
    unittest.main()
