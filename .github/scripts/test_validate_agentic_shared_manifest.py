#!/usr/bin/env python3
"""Tests for the consumer manifest validator."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from validate_agentic_shared_manifest import ManifestValidationError, validate_manifest


class ValidateAgenticSharedManifestTests(unittest.TestCase):
    def valid_manifest(self) -> dict:
        return {
            "source": {
                "repository": "ralphke/agentic-shared",
                "version": "v1.0.0",
            },
            "assets": {
                "agents": "managed",
                "skills": "extended",
                "specs": "local",
            },
            "protected_paths": [".github/skills/local/**"],
        }

    def test_accepts_valid_manifest(self) -> None:
        manifest = self.valid_manifest()
        self.assertEqual(validate_manifest(manifest), manifest)

    def test_rejects_unsupported_ownership_mode(self) -> None:
        manifest = self.valid_manifest()
        manifest["assets"]["skills"] = "replace"

        with self.assertRaisesRegex(ManifestValidationError, "assets.skills"):
            validate_manifest(manifest)

    def test_rejects_unsafe_protected_path(self) -> None:
        manifest = self.valid_manifest()
        manifest["protected_paths"] = ["../private"]

        with self.assertRaisesRegex(ManifestValidationError, "traverse parents"):
            validate_manifest(manifest)

    def test_rejects_duplicate_protected_paths(self) -> None:
        manifest = self.valid_manifest()
        manifest["protected_paths"] = [
            ".github/skills/local/**",
            ".github/skills/local/**",
        ]

        with self.assertRaisesRegex(ManifestValidationError, "duplicates"):
            validate_manifest(manifest)

    def test_rejects_missing_source_version(self) -> None:
        manifest = self.valid_manifest()
        del manifest["source"]["version"]

        with self.assertRaisesRegex(ManifestValidationError, "source.version"):
            validate_manifest(manifest)

    def test_cli_validates_yaml_file(self) -> None:
        script = Path(__file__).with_name("validate_agentic_shared_manifest.py")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as file:
            yaml.safe_dump(self.valid_manifest(), file)
            manifest_path = file.name

        result = subprocess.run(
            [sys.executable, str(script), manifest_path],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Manifest valid", result.stdout)


if __name__ == "__main__":
    unittest.main()
