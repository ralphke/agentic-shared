"""Check skill generator consistency and exercise OpenSpec in an isolated project."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class FabricOpenSpecCliTests(unittest.TestCase):
    def test_skill_generator_versions_are_consistent_per_author(self) -> None:
        authored_skills: dict[str, list[tuple[Path, object]]] = {}
        for path in sorted((ROOT / ".github" / "skills").rglob("SKILL.md")):
            if "local" in path.relative_to(ROOT / ".github" / "skills").parts:
                continue
            sections = path.read_text(encoding="utf-8").split("---", 2)
            self.assertEqual(len(sections), 3, f"{path}: missing YAML frontmatter")
            frontmatter = yaml.safe_load(sections[1])
            self.assertIsInstance(frontmatter, dict, f"{path}: invalid frontmatter")
            metadata = frontmatter.get("metadata", {})
            self.assertIsInstance(metadata, dict, f"{path}: invalid metadata")
            author = metadata.get("author")
            if author is None:
                self.assertNotIn("generatedBy", metadata, f"{path}: generator has no author")
                continue
            self.assertIsInstance(author, str, f"{path}: invalid author")
            self.assertTrue(author.strip(), f"{path}: empty author")
            authored_skills.setdefault(author, []).append((path, metadata.get("generatedBy")))

        self.assertIn("openspec", authored_skills, "No OpenSpec-authored skills found")
        for author, skills in authored_skills.items():
            if author != "openspec" and all(version is None for _, version in skills):
                continue
            expected = skills[0][1]
            for path, version in skills:
                with self.subTest(author=author, skill=path):
                    self.assertIsInstance(version, str, f"{path}: missing/invalid generatedBy")
                    self.assertTrue(version.strip(), f"{path}: empty generatedBy")
                    self.assertEqual(
                        version, expected,
                        f"{author}: {path} generator differs from {skills[0][0]}",
                    )

    def test_isolated_change_discovery_and_instructions(self) -> None:
        executable = shutil.which("openspec")
        self.assertIsNotNone(executable, "OpenSpec CLI is required for compatibility testing")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            environment = os.environ.copy()
            environment.update(
                {
                    "HOME": str(root),
                    "USERPROFILE": str(root),
                    "XDG_CONFIG_HOME": str(root / "config"),
                    "APPDATA": str(root / "appdata"),
                    "OPENSPEC_TELEMETRY": "0",
                    "CI": "1",
                }
            )

            def invoke(*args: str) -> str:
                result = subprocess.run(
                    [executable, *args],
                    cwd=root,
                    env=environment,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                return result.stdout

            invoke("init", "--tools", "none", "--no-copilot-cloud")
            context = json.loads(invoke("context", "--json"))
            self.assertEqual(Path(context["root"]["path"]).resolve(), root.resolve())
            invoke("new", "change", "compatibility-test")
            status = json.loads(invoke("status", "--change", "compatibility-test", "--json"))
            proposal = next(item for item in status["artifacts"] if item["id"] == "proposal")
            self.assertEqual(proposal["status"], "ready")
            instructions = json.loads(
                invoke("instructions", "proposal", "--change", "compatibility-test", "--json")
            )
            self.assertEqual(instructions["artifactId"], "proposal")
            self.assertTrue(instructions["template"])
            self.assertEqual(
                Path(instructions["resolvedOutputPath"]).resolve(),
                (root / "openspec" / "changes" / "compatibility-test" / "proposal.md").resolve(),
            )


if __name__ == "__main__":
    unittest.main()
