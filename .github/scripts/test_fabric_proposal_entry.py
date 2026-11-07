"""Contract tests for the separate Fabric proposal entry point."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class FabricProposalEntryTests(unittest.TestCase):
    def test_fabric_proposal_preserves_planning_and_acceptance_boundaries(self) -> None:
        content = (
            ROOT / ".github" / "skills" / "fabric-propose" / "SKILL.md"
        ).read_text(encoding="utf-8")
        for expected in (
            "name: fabric-propose",
            "check_openspec_compatibility.py",
            "Pre-Capture Intake Decision",
            "`idea-to-spec`",
            "obtain explicit acceptance before design",
            "`spec-to-design`",
            "separate explicit",
            "do not claim",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected.lower(), content.lower())

    def test_default_and_standalone_modes_do_not_disable_repository_controls(self) -> None:
        content = (
            ROOT / ".github" / "instructions" / "sdlc-fabric.instructions.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Existing Fabric consumers use Fabric mode by default.", content)
        self.assertIn("explicitly select standalone OpenSpec", content)
        self.assertIn("does not bypass", content)
        self.assertIn("`fabric-propose`", content)


if __name__ == "__main__":
    unittest.main()
