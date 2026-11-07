#!/usr/bin/env python3
"""Tests for three-way consumer synchronization."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sync_agentic_shared import SyncConflictError, synchronize


class SyncAgenticSharedTests(unittest.TestCase):
    def manifest(self) -> dict:
        return {
            "source": {
                "repository": "ralphke/agentic-shared",
                "version": "v1.0.0",
            },
            "assets": {"skills": "managed"},
            "protected_paths": [".github/skills/local/**"],
        }

    def write(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_updates_unmodified_shared_file_and_preserves_local_extension(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_source = root / "old"
            new_source = root / "new"
            destination = root / "destination"
            self.write(old_source, ".github/skills/shared.md", "old")
            self.write(new_source, ".github/skills/shared.md", "new")
            self.write(destination, ".github/skills/shared.md", "old")
            self.write(destination, ".github/skills/local/custom.md", "consumer")

            changed = synchronize(
                self.manifest(), old_source, new_source, destination, "v1.1.0"
            )

            self.assertEqual(changed, [Path(".github/skills/shared.md")])
            self.assertEqual(
                (destination / ".github/skills/shared.md").read_text(encoding="utf-8"),
                "new",
            )
            self.assertEqual(
                (destination / ".github/skills/local/custom.md").read_text(
                    encoding="utf-8"
                ),
                "consumer",
            )

    def test_copies_file_new_in_shared_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_source = root / "old"
            new_source = root / "new"
            destination = root / "destination"
            self.write(new_source, ".github/skills/new.md", "new")

            changed = synchronize(
                self.manifest(), old_source, new_source, destination, "v1.1.0"
            )

            self.assertEqual(changed, [Path(".github/skills/new.md")])
            self.assertEqual(
                (destination / ".github/skills/new.md").read_text(encoding="utf-8"),
                "new",
            )

    def test_retires_shared_prompt_and_preserves_local_prompt_extension(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_source = root / "old"
            new_source = root / "new"
            destination = root / "destination"
            manifest = self.manifest()
            manifest["assets"] = {"skills": "managed", "prompts": "extended"}
            manifest["protected_paths"].append(".github/prompts/local/**")
            self.write(
                old_source,
                ".github/prompts/opsx-apply.prompt.md",
                "shared prompt wrapper",
            )
            self.write(
                new_source,
                ".github/skills/openspec-propose/SKILL.md",
                "replacement skill",
            )
            self.write(
                destination,
                ".github/prompts/opsx-apply.prompt.md",
                "shared prompt wrapper",
            )
            self.write(
                destination,
                ".github/prompts/local/custom.prompt.md",
                "consumer prompt",
            )

            changed = synchronize(
                manifest, old_source, new_source, destination, "v1.1.0"
            )

            self.assertEqual(
                changed,
                [
                    Path(".github/prompts/opsx-apply.prompt.md"),
                ],
            )
            self.assertFalse(
                (destination / ".github/prompts/opsx-apply.prompt.md").exists()
            )
            self.assertFalse(
                (destination / ".github/skills/openspec-propose/SKILL.md").exists()
            )
            self.assertEqual(
                (destination / ".github/prompts/local/custom.prompt.md").read_text(
                    encoding="utf-8"
                ),
                "consumer prompt",
            )

    def test_blocks_conflict_without_partial_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_source = root / "old"
            new_source = root / "new"
            destination = root / "destination"
            self.write(old_source, ".github/skills/a.md", "old-a")
            self.write(old_source, ".github/skills/b.md", "old-b")
            self.write(new_source, ".github/skills/a.md", "new-a")
            self.write(new_source, ".github/skills/b.md", "new-b")
            self.write(destination, ".github/skills/a.md", "old-a")
            self.write(destination, ".github/skills/b.md", "consumer-b")

            with self.assertRaises(SyncConflictError):
                synchronize(
                    self.manifest(), old_source, new_source, destination, "v1.1.0"
                )

            self.assertEqual(
                (destination / ".github/skills/a.md").read_text(encoding="utf-8"),
                "old-a",
            )

    def test_recovers_missing_managed_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_source = root / "old"
            new_source = root / "new"
            destination = root / "destination"
            self.write(old_source, ".github/skills/shared.md", "old")
            self.write(new_source, ".github/skills/shared.md", "new")

            changed = synchronize(
                self.manifest(), old_source, new_source, destination, "v1.1.0"
            )

            self.assertEqual(changed, [Path(".github/skills/shared.md")])
            self.assertEqual(
                (destination / ".github/skills/shared.md").read_text(encoding="utf-8"),
                "new",
            )

    def test_removed_openspec_skill_requires_review_without_partial_writes(self) -> None:
        for content in ("old", "consumer customization"):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                old_source, new_source, destination = (
                    root / "old", root / "new", root / "destination"
                )
                skill = ".github/skills/openspec-propose/SKILL.md"
                self.write(old_source, skill, "old")
                self.write(destination, skill, content)
                self.write(old_source, ".github/skills/other.md", "old")
                self.write(new_source, ".github/skills/other.md", "new")
                self.write(destination, ".github/skills/other.md", "old")
                manifest = self.manifest()

                with self.assertRaisesRegex(SyncConflictError, "reviewed migration"):
                    synchronize(manifest, old_source, new_source, destination, "v1.1.0")

                self.assertEqual((destination / skill).read_text(encoding="utf-8"), content)
                self.assertEqual(
                    (destination / ".github/skills/other.md").read_text(encoding="utf-8"),
                    "old",
                )
                self.assertEqual(manifest["source"]["version"], "v1.0.0")

    def test_consumer_owned_openspec_skill_is_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_source, new_source, destination = (
                root / "old", root / "new", root / "destination"
            )
            skill = ".github/skills/openspec-apply-change/SKILL.md"
            self.write(new_source, skill, "new shared")
            self.write(destination, skill, "consumer owned")

            with self.assertRaisesRegex(SyncConflictError, "reviewed migration"):
                synchronize(self.manifest(), old_source, new_source, destination, "v1.1.0")

            self.assertEqual(
                (destination / skill).read_text(encoding="utf-8"), "consumer owned"
            )

    def test_customized_openspec_skill_update_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_source, new_source, destination = (
                root / "old", root / "new", root / "destination"
            )
            skill = ".github/skills/openspec-propose/SKILL.md"
            self.write(old_source, skill, "old")
            self.write(new_source, skill, "new")
            self.write(destination, skill, "customized")

            with self.assertRaises(SyncConflictError):
                synchronize(self.manifest(), old_source, new_source, destination, "v1.1.0")

            self.assertEqual(
                (destination / skill).read_text(encoding="utf-8"), "customized"
            )

    def test_protected_openspec_skill_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_source, new_source, destination = (
                root / "old", root / "new", root / "destination"
            )
            skill = ".github/skills/openspec-propose/SKILL.md"
            self.write(old_source, skill, "old")
            self.write(destination, skill, "consumer")
            manifest = self.manifest()
            manifest["protected_paths"].append(".github/skills/openspec-propose/**")

            self.assertEqual(
                synchronize(manifest, old_source, new_source, destination, "v1.1.0"),
                [],
            )
            self.assertEqual((destination / skill).read_text(encoding="utf-8"), "consumer")


if __name__ == "__main__":
    unittest.main()
