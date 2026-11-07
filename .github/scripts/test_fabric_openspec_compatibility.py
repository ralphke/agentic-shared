"""Tests for the supported Fabric OpenSpec integration versions."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "software-fabric-kickoff"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS))

from check_openspec_compatibility import CompatibilityError, check_versions, read_version


class FabricOpenSpecCompatibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = {
            "supportedOpenSpecVersions": ["1.16.0"],
            "minimumNodeMajor": 26,
        }

    def test_supported_versions_pass(self) -> None:
        check_versions("v26.0.0", "1.16.0", self.config)

    def test_unsupported_openspec_version_fails(self) -> None:
        with self.assertRaisesRegex(CompatibilityError, "unsupported OpenSpec version 1.16.1"):
            check_versions("v26.0.0", "1.16.1", self.config)

    def test_unsupported_or_malformed_node_version_fails(self) -> None:
        for version in ("v25.0.0", "not-a-version"):
            with self.subTest(version=version):
                with self.assertRaises(CompatibilityError):
                    check_versions(version, "1.16.0", self.config)

    def test_missing_command_is_reported(self) -> None:
        with patch("check_openspec_compatibility.shutil.which", return_value=None):
            with self.assertRaisesRegex(CompatibilityError, "cannot run openspec --version"):
                read_version("openspec")


if __name__ == "__main__":
    unittest.main()
