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

    def test_blocks_local_deletion_of_managed_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_source = root / "old"
            new_source = root / "new"
            destination = root / "destination"
            self.write(old_source, ".github/skills/shared.md", "old")
            self.write(new_source, ".github/skills/shared.md", "new")

            with self.assertRaises(SyncConflictError):
                synchronize(
                    self.manifest(), old_source, new_source, destination, "v1.1.0"
                )


if __name__ == "__main__":
    unittest.main()
