"""Reviewed migration must preserve ownership boundaries before any writes."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml
from sync_agentic_shared import SyncConflictError, synchronize
from validate_agentic_shared_manifest import validate_manifest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RETIRED = ".github/skills/openspec-propose/SKILL.md"
REPLACEMENT = ".github/skills/openspec-propose/SKILL.md"
FABRIC = ".github/skills/fabric-propose/SKILL.md"
OTHER = ".github/skills/other/SKILL.md"


def digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class ReviewedMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.old, self.new, self.consumer, self.upstream = (
            self.root / name for name in ("old", "new", "consumer", "upstream")
        )
        self.manifest = validate_manifest(yaml.safe_load(
            (REPOSITORY_ROOT / ".agentic-shared.example.yml").read_text(encoding="utf-8")))
        for root in (self.old, self.consumer):
            self.write(root, RETIRED, "former shared")
            self.write(root, OTHER, "old other")
        self.write(self.new, OTHER, "new other")
        self.write(self.new, FABRIC, "Fabric orchestration")
        self.write(self.upstream, REPLACEMENT, "upstream generated")
        self.review = self.make_review()

    def write(self, root: Path, relative: str, content: str) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def make_review(self) -> dict:
        return {
            "schema_version": 1,
            "repository": self.manifest["source"]["repository"],
            "from_version": self.manifest["source"]["version"],
            "to_version": "v2.0.0",
            "openspec_version": "1.16.0",
            "reviewed_by": "migration-reviewer",
            "review_reference": "review/42",
            "files": [{
                "path": RETIRED, "sha256": digest("former shared"),
                "replacement_path": REPLACEMENT,
                "replacement_sha256": digest("upstream generated"),
                "fabric_path": FABRIC,
                "fabric_sha256": digest("Fabric orchestration"),
            }],
        }

    def sync(self) -> list[Path]:
        return synchronize(self.manifest, self.old, self.new, self.consumer,
                           "v2.0.0", self.review, self.upstream)

    def snapshot(self) -> dict[str, bytes]:
        return {path.relative_to(self.consumer).as_posix(): path.read_bytes()
                for path in self.consumer.rglob("*") if path.is_file()}

    def assert_blocked(self) -> None:
        before = self.snapshot()
        version = self.manifest["source"]["version"]
        with self.assertRaises(SyncConflictError):
            self.sync()
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.manifest["source"]["version"], version)

    def test_success_replaces_unchanged_skill_and_preserves_local_data(self) -> None:
        preserved = {
            ".github/skills/local/custom.md": "extension",
            "openspec/config.yaml": "consumer config",
            "openspec/specs/product/spec.md": "product",
            "openspec/changes/active/tasks.md": "active tasks",
        }
        for relative, content in preserved.items():
            self.write(self.consumer, relative, content)
            self.write(self.new, relative, "do not sync")
        changed = self.sync()
        self.assertIn(Path(RETIRED), changed)
        self.assertEqual((self.consumer / RETIRED).read_text(), "upstream generated")
        self.assertEqual((self.consumer / FABRIC).read_text(), "Fabric orchestration")
        for relative, content in preserved.items():
            self.assertEqual((self.consumer / relative).read_text(), content)
        self.assertEqual(self.manifest["source"]["version"], "v2.0.0")

    def test_success_with_renamed_upstream_entry_point(self) -> None:
        replacement = ".github/skills/openspec-archive/SKILL.md"
        self.write(self.upstream, replacement, "upstream generated")
        self.review["files"][0]["replacement_path"] = replacement
        self.sync()
        self.assertFalse((self.consumer / RETIRED).exists())
        self.assertEqual((self.consumer / replacement).read_text(), "upstream generated")

    def test_missing_replacement_blocks_all_writes(self) -> None:
        (self.upstream / REPLACEMENT).unlink()
        self.assert_blocked()

    def test_both_optional_inputs_are_required_together(self) -> None:
        for review, upstream in ((self.review, None), (None, self.upstream)):
            with self.subTest(upstream=upstream):
                before = self.snapshot()
                version = self.manifest["source"]["version"]
                with self.assertRaises(SyncConflictError):
                    synchronize(self.manifest, self.old, self.new, self.consumer,
                                "v2.0.0", review, upstream)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.manifest["source"]["version"], version)

    def test_missing_fabric_blocks_all_writes(self) -> None:
        (self.new / FABRIC).unlink()
        self.assert_blocked()

    def test_customization_and_protection_cannot_be_overridden(self) -> None:
        self.write(self.consumer, RETIRED, "consumer customization")
        self.assert_blocked()
        self.write(self.consumer, RETIRED, "former shared")
        self.manifest["protected_paths"].append(".github/skills/openspec-propose/**")
        self.assert_blocked()

    def test_replacement_collision_cannot_be_overridden(self) -> None:
        replacement = ".github/skills/openspec-archive/SKILL.md"
        self.review["files"][0]["replacement_path"] = replacement
        self.write(self.upstream, replacement, "upstream generated")
        self.write(self.consumer, replacement, "consumer owned")
        self.assert_blocked()

    def test_protected_renamed_replacement_cannot_be_written(self) -> None:
        replacement = ".github/skills/openspec-archive/SKILL.md"
        self.review["files"][0]["replacement_path"] = replacement
        self.write(self.upstream, replacement, "upstream generated")
        self.manifest["protected_paths"].append(".github/skills/openspec-archive/**")
        self.assert_blocked()

    def test_existing_identical_renamed_replacement_is_preserved(self) -> None:
        replacement = ".github/skills/openspec-archive/SKILL.md"
        self.review["files"][0]["replacement_path"] = replacement
        self.write(self.upstream, replacement, "upstream generated")
        self.write(self.consumer, replacement, "upstream generated")
        changed = self.sync()
        self.assertNotIn(Path(replacement), changed)
        self.assertFalse((self.consumer / RETIRED).exists())

    def test_linked_replacement_is_rejected(self) -> None:
        replacement_file = self.upstream / REPLACEMENT
        replacement_file.unlink()
        outside = self.root / "outside.md"
        outside.write_text("upstream generated", encoding="utf-8")
        try:
            replacement_file.symlink_to(outside)
        except OSError as error:
            self.skipTest(f"symlink creation unavailable: {error}")
        self.assert_blocked()

    def test_unrelated_threeway_conflict_blocks_migration(self) -> None:
        self.write(self.consumer, OTHER, "consumer customization")
        self.assert_blocked()

    def test_invalid_headers_block_before_writes(self) -> None:
        for field, value in (
            ("schema_version", True), ("repository", "other/repository"),
            ("from_version", "v0.0.0"), ("to_version", "v9.0.0"),
            ("openspec_version", "1.17.0"), ("reviewed_by", ""),
            ("review_reference", ""), ("files", []),
        ):
            with self.subTest(field=field):
                self.review = self.make_review()
                self.review[field] = value
                self.assert_blocked()

    def test_stale_hashes_and_unsafe_paths_block_before_writes(self) -> None:
        for field, value in (
            ("sha256", digest("wrong")), ("replacement_sha256", "not a hash"),
            ("fabric_sha256", digest("wrong")), ("path", "../escape"),
            ("replacement_path", ".github/skills/openspec-a/../../escape"),
            ("fabric_path", RETIRED),
        ):
            with self.subTest(field=field):
                self.review = self.make_review()
                self.review["files"][0][field] = value
                self.assert_blocked()

    def test_review_must_cover_all_files_without_duplicates(self) -> None:
        self.review["files"].append(self.review["files"][0].copy())
        self.assert_blocked()
        self.review = self.make_review()
        auxiliary = ".github/skills/openspec-propose/reference.md"
        self.write(self.old, auxiliary, "shared reference")
        self.write(self.consumer, auxiliary, "shared reference")
        self.assert_blocked()

    def test_protected_or_local_fabric_requires_installed_matching_entry(self) -> None:
        self.manifest["protected_paths"].append(".github/skills/fabric-propose/**")
        self.assert_blocked()
        self.write(self.consumer, FABRIC, "Fabric orchestration")
        self.sync()

    def test_target_release_never_distributes_upstream_skills(self) -> None:
        self.write(self.new, RETIRED, "parent worktree upstream skill")
        self.write(self.new, ".github/skills/openspec-new/SKILL.md", "not shared")
        self.sync()
        self.assertEqual((self.consumer / RETIRED).read_text(), "upstream generated")
        self.assertFalse((self.consumer / ".github/skills/openspec-new/SKILL.md").exists())

    def test_guide_documents_the_executable_contract_and_safe_rollback(self) -> None:
        guide = (REPOSITORY_ROOT / "doc/fabric-consumer-migration.md").read_text(
            encoding="utf-8")
        for option in ("--openspec-migration", "--upstream-source", "--target-version"):
            self.assertIn(option, guide)
        for field in self.review:
            self.assertIn(field, guide)
        for field in self.review["files"][0]:
            self.assertIn(field, guide)
        for invariant in ("specs: local", "openspec/changes/**", "--store agentic-shared",
                          "Node.js 26+", "1.16.0", "pre-migration backup",
                          "later customizations", "XDG_DATA_HOME", "LOCALAPPDATA"):
            self.assertIn(invariant, guide)

    def test_cli_requires_tangible_review_and_does_not_update_manifest_on_failure(self) -> None:
        manifest_path = self.root / ".agentic-shared.yml"
        manifest_path.write_text(yaml.safe_dump(self.manifest), encoding="utf-8")
        review_path = self.root / "review.json"
        review_path.write_text(json.dumps(self.review), encoding="utf-8")
        arguments = [
            sys.executable, "-B", str(REPOSITORY_ROOT / ".github/scripts/sync_agentic_shared.py"),
            "--manifest", str(manifest_path), "--old-source", str(self.old),
            "--new-source", str(self.new), "--destination", str(self.consumer),
            "--target-version", "v2.0.0",
        ]
        before = manifest_path.read_bytes()
        result = subprocess.run(arguments, capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(manifest_path.read_bytes(), before)
        result = subprocess.run(arguments + [
            "--openspec-migration", str(review_path), "--upstream-source", str(self.upstream),
        ], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(yaml.safe_load(manifest_path.read_text())["source"]["version"],
                         "v2.0.0")


if __name__ == "__main__":
    unittest.main()
